const express = require('express');
const { EmailUser, GoogleUser, GithubUser, findUserAcrossCollections } = require('../models/User');
const { authenticateToken } = require('../middleware/auth');
const { profileUpdateValidation, handleValidationErrors } = require('../middleware/validation');

const router = express.Router();

// Get user profile (protected route)
router.get('/profile', authenticateToken, async (req, res) => {
  try {
    res.json({
      success: true,
      data: {
        user: req.user.toPublicJSON()
      }
    });
  } catch (error) {
    console.error('Get profile error:', error);
    res.status(500).json({
      success: false,
      message: 'Error fetching profile'
    });
  }
});

// Update user profile (protected route)
router.put('/profile', authenticateToken, profileUpdateValidation, handleValidationErrors, async (req, res) => {
  try {
    const { firstName, lastName, email } = req.body;
    const user = req.user;

    // Check if email is being changed and if it's already taken
    if (email && email !== user.email) {
      const { user: existingUser } = await findUserAcrossCollections(email);
      if (existingUser) {
        return res.status(400).json({
          success: false,
          message: 'Email is already taken'
        });
      }
      user.email = email;
    }

    // Update other fields
    if (firstName) user.firstName = firstName;
    if (lastName) user.lastName = lastName;

    await user.save();

    res.json({
      success: true,
      message: 'Profile updated successfully',
      data: {
        user: user.toPublicJSON()
      }
    });
  } catch (error) {
    console.error('Update profile error:', error);
    res.status(500).json({
      success: false,
      message: 'Error updating profile'
    });
  }
});

// Delete user account (protected route)
router.delete('/account', authenticateToken, async (req, res) => {
  try {
    // Delete user from the appropriate collection
    let deleted = await EmailUser.findByIdAndDelete(req.user._id);
    if (!deleted) {
      deleted = await GoogleUser.findByIdAndDelete(req.user._id);
    }
    if (!deleted) {
      deleted = await GithubUser.findByIdAndDelete(req.user._id);
    }
    
    res.json({
      success: true,
      message: 'Account deleted successfully'
    });
  } catch (error) {
    console.error('Delete account error:', error);
    res.status(500).json({
      success: false,
      message: 'Error deleting account'
    });
  }
});

// Get user statistics (protected route)
router.get('/stats', authenticateToken, async (req, res) => {
  try {
    const user = req.user;
    
    // You can add more statistics here based on your app's needs
    const stats = {
      accountCreated: user.createdAt,
      lastLogin: user.lastLogin,
      loginMethod: user.loginMethod,
      isEmailVerified: user.isEmailVerified
    };

    res.json({
      success: true,
      data: {
        stats
      }
    });
  } catch (error) {
    console.error('Get stats error:', error);
    res.status(500).json({
      success: false,
      message: 'Error fetching statistics'
    });
  }
});

module.exports = router;
