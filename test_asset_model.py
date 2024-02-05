import os
from unittest import TestCase

from models import db, User, Asset, UserAssetComparison
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

os.environ['DATABASE_URL'] = "postgresql:///mcm_test_db"

from app import app

db.create_all()

class AssetModelTestCase(TestCase):
    """Test Asset Model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Asset.query.delete()
        UserAssetComparison.query.delete()

        self.client = app.test_client()

        self.testasset = Asset(name='FakeAsset', ticker='FAKE', price=100.00, market_cap=1000.00)

        db.session.add(self.testasset)
        db.session.commit()

    def test_repr(self):
        """Tests that the __repr__ method works as expected."""

        self.assertEqual(repr(self.testasset), f"<Asset: id={self.testasset.id}, Name={self.testasset.name}, Ticker={self.testasset.ticker}, Price={self.testasset.price}, Market Cap={self.testasset.market_cap}>")
