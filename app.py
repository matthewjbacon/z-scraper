from flask import Flask, request, jsonify
from requests_html import HTMLSession

app = Flask(__name__)

@app.route("/scrape_zillow", methods=["POST"])
def scrape_zillow():
    try:
        data = request.get_json()
        zillow_url = data.get("url")

        if not zillow_url or "zillow.com" not in zillow_url:
            return jsonify({"error": "Invalid or missing Zillow URL"}), 400

        session = HTMLSession()
        response = session.get(zillow_url)
        # Add sleep to let JS load fully
        response.html.render(timeout=30, sleep=3)

        address = response.html.find('[data-testid="home-details-summary-headline"]', first=True)
        price = response.html.find('[data-testid="price"]', first=True)

        # Updated selector for beds, baths, sqft list items
        facts = response.html.find('ul.StyledHomeDetailsList-c11n-8-68-3__sc-17h3l6a-0 li')

        beds = facts[0].text if len(facts) > 0 else None
        baths = facts[1].text if len(facts) > 1 else None
        sqft = facts[2].text if len(facts) > 2 else None

        return jsonify({
            "address": address.text if address else None,
            "price": price.text if price else None,
            "beds": beds,
            "baths": baths,
            "sqft": sqft,
            "source_url": zillow_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)