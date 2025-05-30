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
        response.html.render(timeout=60, sleep=5, scrolldown=3)

        address = response.html.find('h1.ds-address-container', first=True)
        price = response.html.find('span.ds-value', first=True)
        facts = response.html.find('span.ds-bed-bath-living-area span')

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