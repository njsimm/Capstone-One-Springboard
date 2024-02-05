import os

from unittest import TestCase

from models import db, User, Asset, UserAssetComparison
from flask import url_for
from flask_bcrypt import Bcrypt
from constants import CURRENT_USER_KEY
bcrypt = Bcrypt()

os.environ['DATABASE_URL'] = "postgresql:///mcm_test_db"

from app import app

db.drop_all()
db.create_all()

class ViewTestCase(TestCase):
    """Test view functions."""
    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Asset.query.delete()
        UserAssetComparison.query.delete()

        self.client = app.test_client()

        self.testuser1 = User.signup(username='testuser', password='testpassword')
        self.testuser1.password = bcrypt.generate_password_hash(self.testuser1.password).decode('UTF-8')

        self.testuser2 = User.signup(username='testuser2', password='testpassword2')
        self.testuser2.password = bcrypt.generate_password_hash(self.testuser2.password).decode('UTF-8')

        db.session.add_all([self.testuser1, self.testuser2])
        db.session.commit()

        self.testasset1 = Asset(name='FakeAsset1', ticker='FAKE1', price=100.00, market_cap=1000.00)

        self.testasset2 = Asset(name='FakeAsset2', ticker='FAKE2', price=200.00, market_cap=2000.00)

        db.session.add_all([self.testasset1, self.testasset2])
        db.session.commit()

        self.uac = UserAssetComparison(user_id=self.testuser1.id, asset_id_1=self.testasset1.id, asset_1_price_at_comparison=self.testasset1.price, asset_1_market_cap_at_comparison=self.testasset1.market_cap, asset_id_2=self.testasset2.id, asset_2_price_at_comparison=self.testasset2.price, asset_2_market_cap_at_comparison=self.testasset2.market_cap, comparison_timestamp='2018-01-01 00:00:00', percent_difference=100.00)
        db.session.add(self.uac)
        db.session.commit()
    
    def tearDown(self):
        """Clean up / tear down."""

        db.session.rollback()

    def test_homepage_logged_in(self):
        """Test homepage view with logged in user."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_USER_KEY] = self.testuser1.id
            
            resp = c.get('/')
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, url_for('dashboard', _external=True))

    def test_homepage_logged_out(self):
        """Test homepage view with logged out user."""
        with self.client as c:
            resp = c.get('/')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Login', html)
            self.assertIn('Signup', html)

    def test_logout(self):
        """Test logout view."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_USER_KEY] = self.testuser1.id

            resp = c.post('/logout', follow_redirects=False)
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, url_for('home_page', _external=True))

            
            resp = c.post('/logout', follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"Goodbye, {self.testuser1.username}!", html)

    def test_get_user_history(self):
        """Test get_user_history view."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_USER_KEY] = self.testuser1.id

            resp = c.get('/get_user_history')
            html = resp.get_data(as_text=True)
            self.assertIn('FakeAsset1', html)
            self.assertIn('FakeAsset2', html)


        
    
    