import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

PORT = int(os.environ.get('PORT', 5000))

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

CORS(app)


class Section(db.Model):
  __tablename__ = 'sections'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  recommendations = db.relationship("Recommendation")

  def format(self):
      return {
          'id': self.id,
          'name': self.name
        }

class Recommendation(db.Model):
  __tablename__ = 'recommendations'
  id = db.Column(db.Integer, primary_key=True)
  section_id = db.Column(db.Integer, db.ForeignKey('sections.id'))
  text = db.Column(db.String)
  number = db.Column(db.Integer)
  ongoing = db.Column(db.Boolean)
  unsure = db.Column(db.Boolean)
  done = db.Column(db.Boolean)
  status = db.Column(db.String, default="notStarted")
  link = db.Column(db.String)

  def format(self):
      return {
          'id': self.id,
          'section_id':  self.section_id,
          'text': self.text,
          'number': self.number,
          'ongoing': self.ongoing,
          'unsure': self.unsure,
          'done': self.done,
          'status': self.status,
          'link' : self.link
      }


db.create_all()

@app.route('/sections')
def fetch_sections():
    selection = Section.query.join(Recommendation).all()
    res = []
    for s in selection:
        dic = {'name': s.name}
        dic['recommendations'] = []
        for r in s.recommendations:
            reco = {
                'number': r.number,
                'done': r.done,
                'ongoing': r.ongoing,
                'unsure': r.unsure,
                'text': r.text,
                'status': r.status
            }
            dic['recommendations'].append(reco)

        dic['recommendations'] = sorted(dic["recommendations"], key=lambda x: x['number'])
        res.append(dic)

    return jsonify({
        'success': True,
        'sections': res
    })


@app.route('/recommendations/<status>')
def fetch_ongoing(status):
    selection = Recommendation.query.filter(Recommendation.status == status).all()
    recommendations = [recommendation.format() for recommendation in selection]

    return jsonify({
        'success': True,
        'recommendations': recommendations
    })


@app.route('/stats')
def calculate_stats():
    recommendations = Recommendation.query.all()

    stats = {
        'done': Recommendation.query.filter(Recommendation.status == "done").count(),
        'ongoing': Recommendation.query.filter(Recommendation.status == "ongoing").count(),
        'unsure': Recommendation.query.filter(Recommendation.status == "unsure").count(),
        'notStarted': Recommendation.query.filter(Recommendation.status == "notStarted").count()
    }

    print(stats)

    return jsonify({
        'success': True,
        'stats': stats
    })


if __name__ == "__main__":
    app.run()