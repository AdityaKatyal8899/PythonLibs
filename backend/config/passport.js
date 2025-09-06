const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const GitHubStrategy = require('passport-github2').Strategy;
const { EmailUser, GoogleUser, GithubUser, findUserAcrossCollections, createUserInCollection } = require('../models/User');

// Serialize user for the session
passport.serializeUser((user, done) => {
  done(null, user.id);
});

// Deserialize user from the session
passport.deserializeUser(async (id, done) => {
  try {
    // Find user across all collections by ID
    let user = await EmailUser.findById(id);
    if (!user) {
      user = await GoogleUser.findById(id);
    }
    if (!user) {
      user = await GithubUser.findById(id);
    }
    done(null, user);
  } catch (error) {
    done(error, null);
  }
});

// Google OAuth Strategy
passport.use(new GoogleStrategy({
  clientID: process.env.GOOGLE_CLIENT_ID,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  callbackURL: `${process.env.FRONTEND_URL || 'http://localhost:3000'}/api/auth/google/callback`
}, async (accessToken, refreshToken, profile, done) => {
  try {
    // Check if user already exists in Google LogIns collection
    let user = await GoogleUser.findOne({ googleId: profile.id });

    if (user) {
      // User exists, update last login
      user.lastLogin = new Date();
      await user.save();
      return done(null, user);
    }

    // Check if user exists with same email across all collections
    const { user: existingUser, collection } = await findUserAcrossCollections(profile.emails[0].value);

    if (existingUser) {
      // User exists with email but no Google ID, create new entry in Google LogIns
      const newUser = await createUserInCollection({
        email: profile.emails[0].value,
        firstName: existingUser.firstName,
        lastName: existingUser.lastName,
        googleId: profile.id,
        loginMethod: 'google',
        isEmailVerified: true,
        avatar: profile.photos && profile.photos[0] ? profile.photos[0].value : null
      }, 'google');
      return done(null, newUser);
    }

    // Create new user in Google LogIns collection
    const newUser = await createUserInCollection({
      email: profile.emails[0].value,
      firstName: profile.name.givenName || profile.displayName.split(' ')[0],
      lastName: profile.name.familyName || profile.displayName.split(' ').slice(1).join(' ') || '',
      googleId: profile.id,
      loginMethod: 'google',
      isEmailVerified: true, // Google emails are verified
      avatar: profile.photos && profile.photos[0] ? profile.photos[0].value : null
    }, 'google');

    return done(null, newUser);
  } catch (error) {
    console.error('Google OAuth error:', error);
    return done(error, null);
  }
}));

// GitHub OAuth Strategy
passport.use(new GitHubStrategy({
  clientID: process.env.GITHUB_CLIENT_ID,
  clientSecret: process.env.GITHUB_CLIENT_SECRET,
  callbackURL: `${process.env.FRONTEND_URL || 'http://localhost:3000'}/api/auth/github/callback`
}, async (accessToken, refreshToken, profile, done) => {
  try {
    // Check if user already exists in GitHub LogIns collection
    let user = await GithubUser.findOne({ githubId: profile.id });

    if (user) {
      // User exists, update last login
      user.lastLogin = new Date();
      await user.save();
      return done(null, user);
    }

    // Get email from GitHub profile
    const email = profile.emails && profile.emails[0] ? profile.emails[0].value : null;
    
    if (email) {
      // Check if user exists with same email across all collections
      const { user: existingUser, collection } = await findUserAcrossCollections(email);

      if (existingUser) {
        // User exists with email but no GitHub ID, create new entry in GitHub LogIns
        const newUser = await createUserInCollection({
          email: email,
          firstName: existingUser.firstName,
          lastName: existingUser.lastName,
          githubId: profile.id,
          loginMethod: 'github',
          isEmailVerified: !!email,
          avatar: profile.photos && profile.photos[0] ? profile.photos[0].value : null
        }, 'github');
        return done(null, newUser);
      }
    }

    // Create new user in GitHub LogIns collection
    const newUser = await createUserInCollection({
      email: email || `${profile.username}@github.com`, // Fallback email
      firstName: profile.displayName ? profile.displayName.split(' ')[0] : profile.username,
      lastName: profile.displayName ? profile.displayName.split(' ').slice(1).join(' ') : '',
      githubId: profile.id,
      loginMethod: 'github',
      isEmailVerified: !!email, // Only verified if we got a real email
      avatar: profile.photos && profile.photos[0] ? profile.photos[0].value : null
    }, 'github');

    return done(null, newUser);
  } catch (error) {
    console.error('GitHub OAuth error:', error);
    return done(error, null);
  }
}));

module.exports = passport;
