import os
from unittest import TestCase

from models import db, User, Asset, UserAssetComparison
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

os.environ['DATABASE_URL'] = "postgresql:///mcm_test_db"

from app import app

db.drop_all()
db.create_all()

class UserModelTestCase(TestCase):
    """Test User Model"""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Asset.query.delete()
        UserAssetComparison.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username='testuser', password='testpassword')

        db.session.add(self.testuser)
        db.session.commit()

    def tearDown(self):
        """Clean up / tear down."""

        db.session.rollback()

    def test_repr(self):
        """Tests that the __repr__ method works as expected."""

        self.assertEqual(repr(self.testuser), f"<User: id={self.testuser.id}, Username={self.testuser.username}>")

    def test_signup_success(self):
        """Tests that the signup class method succeeds as expected."""

        new_user_1 = User.signup(username='newuser', password='newpassword')

        db.session.add(new_user_1)
        db.session.commit()

        self.assertEqual(new_user_1.username, 'newuser')
        self.assertTrue(bcrypt.check_password_hash(new_user_1.password, 'newpassword'))

    def test_signup_fail(self):
        """Tests that the signup class method fails as expected."""
        
        with self.assertRaises(IntegrityError):
            new_user_2 = User.signup(username='testuser', password='newpassword')
            db.session.add(new_user_2)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                raise

    def test_authenticate_success(self):
        """Tests that the authenticate class method succeeds as expected."""

        testuser = User.authenticate(self.testuser.username, entered_login_pwd='testpassword')

        self.assertEqual(testuser, self.testuser)

    def test_authenticate_fail(self):
        """Tests that the authenticate class method fails as expected."""

        testuser = User.authenticate(self.testuser.username, entered_login_pwd='abcdefghijklmonpqrstuvwxz')

        self.assertFalse(testuser)


