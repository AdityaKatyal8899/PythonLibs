const mongoose = require("mongoose");
const bcrypt = require("bcryptjs");

// 🔹 Shared base schema for all providers
const baseUserSchema = {
  email: {
    type: String,
    required: true,
    lowercase: true,
    trim: true,
    match: [
      /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/,
      "Please enter a valid email",
    ],
  },
  password: {
    type: String,
    required: function () {
      // Required only for email signup
      return this.loginMethod === "email";
    },
    minlength: [6, "Password must be at least 6 characters long"],
  },
  firstName: {
    type: String,
    required: true,
    trim: true,
    maxlength: [50, "First name cannot exceed 50 characters"],
  },
  lastName: {
    type: String,
    required: true,
    trim: true,
    maxlength: [50, "Last name cannot exceed 50 characters"],
  },
  googleId: {
    type: String,
  },
  githubId: {
    type: String,
  },
  avatar: {
    type: String,
    default: null,
  },
  isEmailVerified: {
    type: Boolean,
    default: false,
  },
  lastLogin: {
    type: Date,
    default: Date.now,
  },
  loginMethod: {
    type: String,
    enum: ["email", "google", "github"],
    required: true,
  },
};

// 🔹 Create schema
const userSchema = new mongoose.Schema(baseUserSchema, { timestamps: true });

// Indexes for faster lookups
userSchema.index({ email: 1 });
userSchema.index({ googleId: 1 });
userSchema.index({ githubId: 1 });

// Virtual field: full name
userSchema.virtual("fullName").get(function () {
  return `${this.firstName} ${this.lastName}`;
});

// Pre-save hook: hash password
userSchema.pre("save", async function (next) {
  if (!this.isModified("password")) return next();
  try {
    const salt = await bcrypt.genSalt(12);
    this.password = await bcrypt.hash(this.password, salt);
    next();
  } catch (error) {
    next(error);
  }
});

// Compare password method
userSchema.methods.comparePassword = async function (candidatePassword) {
  return bcrypt.compare(candidatePassword, this.password);
};

// Hide sensitive fields in public JSON
userSchema.methods.toPublicJSON = function () {
  const userObject = this.toObject();
  delete userObject.password;
  delete userObject.__v;
  return userObject;
};

// Update last login timestamp
userSchema.methods.updateLastLogin = function () {
  this.lastLogin = new Date();
  return this.save();
};

// 🔹 Multiple models for separate collections
const EmailUser = mongoose.model("EmailUser", userSchema, "Email LogIns"); // <-- emailUsers collection
const GithubUser = mongoose.model("GithubUser", userSchema, "GitHubLogIns"); // <-- githubUsers collection
const GoogleUser = mongoose.model("GoogleUser", userSchema, "GoogleLogIns"); // <-- googleUsers collection

// Helper function to find user across all collections
const findUserAcrossCollections = async (email, googleId = null, githubId = null) => {
  let user = null;
  
  // Search in Email LogIns collection
  if (email) {
    user = await EmailUser.findOne({ email });
    if (user) return { user, collection: 'email' };
  }
  
  // Search in Google LogIns collection
  if (googleId) {
    user = await GoogleUser.findOne({ googleId });
    if (user) return { user, collection: 'google' };
  }
  
  // Search in GitHub LogIns collection
  if (githubId) {
    user = await GithubUser.findOne({ githubId });
    if (user) return { user, collection: 'github' };
  }
  
  return { user: null, collection: null };
};

// Helper function to create user in appropriate collection
const createUserInCollection = async (userData, loginMethod) => {
  switch (loginMethod) {
    case 'email':
      return await EmailUser.create(userData);
    case 'google':
      return await GoogleUser.create(userData);
    case 'github':
      return await GithubUser.create(userData);
    default:
      throw new Error('Invalid login method');
  }
};

module.exports = { 
  EmailUser, 
  GoogleUser, 
  GithubUser, 
  findUserAcrossCollections,
  createUserInCollection
};
