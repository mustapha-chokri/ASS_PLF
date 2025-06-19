from app import create_app, db
from app.models.finance import CashBox
from sqlalchemy import text
import logging

def fix_cash_boxes():
    app = create_app()
    with app.app_context():
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        try:
            # Drop the existing table
            CashBox.__table__.drop(db.engine, checkfirst=True)
            logger.info("Dropped existing cash_boxes table")
            
            # Create the table with the correct structure
            CashBox.__table__.create(db.engine)
            logger.info("Created cash_boxes table with correct structure")
            
            # Verify the table structure
            with db.engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(cash_boxes);")).fetchall()
                logger.info("Cash_boxes table structure:")
                for row in result:
                    logger.info(row)
            
            logger.info("Cash_boxes table has been fixed successfully!")
            
        except Exception as e:
            logger.error(f"Error fixing cash_boxes table: {str(e)}")
            raise

if __name__ == '__main__':
    fix_cash_boxes() 