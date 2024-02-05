import os
from unittest import TestCase

from models import db, User, Asset, UserAssetComparison
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

os.environ['DATABASE_URL'] = "postgresql:///mcm_test_db"

from app import app

db.drop_all()
db.create_all()

class UserAssetComparisonModel(TestCase):
    """Test UserAssetComparison Model."""

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

    def test_repr(self):
        """Tests that the __repr__ method works as expected."""

        self.assertEqual(repr(self.uac), f"<UserAssetComparison: id={self.uac.id}, User ID={self.uac.user_id}, Asset ID 1={self.uac.asset_id_1}, Asset 1 Price={self.uac.asset_1_price_at_comparison}, Asset 1 Market Cap={self.uac.asset_1_market_cap_at_comparison}, Asset ID 2={self.uac.asset_id_2}, Asset 2 Price={self.uac.asset_2_price_at_comparison}, Asset 2 Market Cap={self.uac.asset_2_market_cap_at_comparison}, Comparison Timestamp={self.uac.comparison_timestamp}, Percent Difference={self.uac.percent_difference}>")

    def test_comparison_and_user(self):
        """Tests that the comparison and user relationship works as expected."""

        self.assertEqual(self.uac.user_id, self.testuser1.id)
        self.assertFalse(self.uac.user_id == self.testuser2.id)

    def test_asset_1_and_asset_2_relationship(self):
        """Tests that the asset_1 and asset_2 relationship works as expected."""

        self.assertEqual(self.uac.asset_1, self.testasset1)
        self.assertEqual(self.uac.asset_2, self.testasset2)