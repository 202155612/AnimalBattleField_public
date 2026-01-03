import psycopg2
import database.database as db

from models.models import Ability

def get_abilities(ability_ids=None):
    conn = None
    try:
        conn = db.access()
        with conn:
            with conn.cursor() as cur:
                if ability_ids == None:
                    cur.execute('''
                        SELECT ability_id, name, description, image_file
                        FROM abilities
                    ''')
                elif ability_ids == []:
                    return []
                else:
                    placeholders = ', '.join(['%s'] * len(ability_ids))
                    query = f'''
                        SELECT ability_id, name, description, image_file
                        FROM abilities
                        WHERE ability_id IN ({placeholders})
                    '''
                    cur.execute(query, tuple(ability_ids))

                rows = cur.fetchall()
                return [
                    Ability(ability_id, name, desc, image_file)
                    for ability_id, name, desc, image_file in rows
                ]
    except:
        raise
