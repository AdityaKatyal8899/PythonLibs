const jwt = require('jsonwebtoken');
const { EmailUser, GoogleUser, GithubUser } = require('../models/User');

// Middleware to verify JWT token
const authenticateToken = async (req, res, next) => {
  try {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
      return res.status(401).json({
        success: false,
        message: 'Access token required'
      });
    }

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
        message: 'Invalid token - user not found'
      });
    }

    req.user = user;
    next();
  } catch (error) {
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({
        success: false,
        message: 'Invalid token'
      });
    } else if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        success: false,
        message: 'Token expired'
      });
    }
    
    console.error('Auth middleware error:', error);
    return res.status(500).json({
      success: false,
      message: 'Authentication error'
    });
  }
};

// Optional authentication middleware (doesn't fail if no token)
const optionalAuth = async (req, res, next) => {
  try {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (token) {
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      
      // Find user across all collections by ID
      let user = await EmailUser.findById(decoded.userId);
      if (!user) {
        user = await GoogleUser.findById(decoded.userId);
      }
      if (!user) {
        user = await GithubUser.findById(decoded.userId);
      }
      
      if (user) {
        req.user = user;
      }
    }
    next();
  } catch (error) {
    // Continue without authentication if token is invalid
    next();
  }
};

// Generate JWT token
const generateToken = (userId) => {
  return jwt.sign(
    { userId },
    process.env.JWT_SECRET,
    { expiresIn: process.env.JWT_EXPIRES_IN || '7d' }
  );
};

module.exports = {
  authenticateToken,
  optionalAuth,
  generateToken
};
