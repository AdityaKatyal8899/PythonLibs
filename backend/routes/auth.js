const express = require('express');
const passport = require('passport');
const { EmailUser, GoogleUser, GithubUser, findUserAcrossCollections, createUserInCollection } = require('../models/User');
const { generateToken } = require('../middleware/auth');
const { signupValidation, signinValidation, handleValidationErrors } = require('../middleware/validation');

const router = express.Router();

// Email/Password Signup
router.post('/signup', signupValidation, handleValidationErrors, async (req, res) => {
  try {
    const { email, password, firstName, lastName } = req.body;

    // Check if user already exists across all collections
    const { user: existingUser } = await findUserAcrossCollections(email);
    if (existingUser) {
      return res.status(400).json({
        success: false,
        message: 'User with this email already exists'
      });
    }

    // Create new user in Email LogIns collection
    const user = await createUserInCollection({
      email,
      password,
      firstName,
      lastName,
      loginMethod: 'email'
    }, 'email');

    // Generate token
    const token = generateToken(user._id);

    // Update last login
    await user.updateLastLogin();

    res.status(201).json({
      success: true,
      message: 'User created successfully',
      data: {
        user: user.toPublicJSON(),
        token
      }
    });
  } catch (error) {
    console.error('Signup error:', error);
    res.status(500).json({
      success: false,
      message: 'Error creating user',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Internal server error'
    });
  }
});

// Email/Password Signin
router.post('/signin', signinValidation, handleValidationErrors, async (req, res) => {
  try {
    const { email, password } = req.body;

    // Find user by email across all collections
    const { user, collection } = await findUserAcrossCollections(email);
    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Invalid email or password'
      });
    }

    // Check if user has password (OAuth users might not have password)
    if (!user.password) {
      return res.status(401).json({
        success: false,
        message: 'This account was created with OAuth. Please use OAuth to sign in.'
      });
    }

    // Verify password
    const isPasswordValid = await user.comparePassword(password);
    if (!isPasswordValid) {
      return res.status(401).json({
        success: false,
        message: 'Invalid email or password'
      });
    }

    // Generate token
    const token = generateToken(user._id);

    // Update last login
    await user.updateLastLogin();

    res.json({
      success: true,
      message: 'Login successful',
      data: {
        user: user.toPublicJSON(),
        token
      }
    });
  } catch (error) {
    console.error('Signin error:', error);
    res.status(500).json({
      success: false,
      message: 'Error during signin',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Internal server error'
    });
  }
});

// Get current user profile
router.get('/me', async (req, res) => {
  try {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
      return res.status(401).json({
        success: false,
        message: 'Access token required'
      });
    }

    const jwt = require('jsonwebtoken');
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    // Find user across all collections by ID
    let user = await EmailUser.findById(decoded.userId);
    if (!user) {
      user = await GoogleUser.findById(decoded.userId);
    }
    if (!user) {
      user = await GithubUser.findById(decoded.userId);
    }

    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'User not found'
      });
    }

    res.json({
      success: true,
      data: {
        user: user.toPublicJSON()
      }
    });
  } catch (error) {
    console.error('Get profile error:', error);
    res.status(401).json({
      success: false,
      message: 'Invalid token'
    });
  }
});

// Logout (client-side token removal)
router.post('/logout', (req, res) => {
  res.json({
    success: true,
    message: 'Logged out successfully'
  });
});

// Google OAuth routes
router.get('/google', passport.authenticate('google', {
  scope: ['profile', 'email']
}));

router.get('/google/callback', 
  passport.authenticate('google', { session: false }),
  async (req, res) => {
    try {
      const user = req.user;
      const token = generateToken(user._id);
      
      // Update last login
      await user.updateLastLogin();

      // Redirect to frontend with token
      res.redirect(`${process.env.FRONTEND_URL}/auth/callback?token=${token}&provider=google`);
    } catch (error) {
      console.error('Google OAuth callback error:', error);
      res.redirect(`${process.env.FRONTEND_URL}/auth/error?message=Google authentication failed`);
    }
  }
);

// GitHub OAuth routes
router.get('/github', passport.authenticate('github', {
  scope: ['user:email']
}));

router.get('/github/callback',
  passport.authenticate('github', { session: false }),
  async (req, res) => {
    try {
      const user = req.user;
      const token = generateToken(user._id);
      
      // Update last login
      await user.updateLastLogin();

      // Redirect to frontend with token
      res.redirect(`${process.env.FRONTEND_URL}/auth/callback?token=${token}&provider=github`);
    } catch (error) {
      console.error('GitHub OAuth callback error:', error);
      res.redirect(`${process.env.FRONTEND_URL}/auth/error?message=GitHub authentication failed`);
    }
  }
);

module.exports = router;
