from flask import Flask, render_template, request, redirect, session, url_for, flash, send_file, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import csv
import io
import os
import razorpay

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-this-local-secret-before-live')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'support@pesawala.com')

# Default password: Babul@123
# For live use, set ADMIN_PASSWORD_HASH in environment variables
DEFAULT_ADMIN_PASSWORD = 'Babul@123'
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH')

if not ADMIN_PASSWORD_HASH:
    ADMIN_PASSWORD_HASH = generate_password_hash(DEFAULT_ADMIN_PASSWORD)

# Razorpay keys
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_SUaeyX8tpf3q8T")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "5RW0SRtbp6tv393xPvUUKwX8")

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

SITE = {
    'brand': 'PESAWALA',
    'phone': '+1 3617230932',
    'email': 'support@pesawala.com',
    'city': 'Weber Road, Corpus Christi, Texas',
    'hero_title': 'Boost Your Brand Visibility With Performance-Driven Digital Solutions',
    'hero_subtitle': 'Quantumnts Digital is a modern digital solutions company dedicated to helping businesses grow in the online world. We specialize in delivering smart,'
                     ' creative, and result-driven services that empower brands to build a strong digital presence and reach their target audience effectively.'
                     'At Quantumnts Digital, we believe every business has unique potential.',
    'services': [

        {'title': 'Website Development',
         'desc': 'Responsive business websites, landing pages, and custom portals built for speed and conversion.',
         'icon': 'code-slash', 'img': 'images/services/web.png'},
        {'title': 'SEO Services',
         'desc': 'On-page, technical, local, and content SEO to improve rankings and qualified traffic.',
         'icon': 'search', 'img': 'images/services/seo.png'},
        {'title': 'Social Media Management',
         'desc': 'Platform-specific content planning, creative posting, and performance campaigns.', 'icon': 'share',
         'img': 'images/services/smm.png'},
        {'title': 'Graphic Design',
         'desc': 'Brand visuals, marketing creatives, ad banners, and polished presentation assets.', 'icon': 'palette',
         'img': 'images/services/graphic.png'},
        {'title': 'App Development', 'desc': 'Android and iOS app interfaces with scalable backend integration.',
         'icon': 'phone', 'img': 'images/services/app.png'},
        {'title': 'ERP / CRM Development',
         'desc': 'Custom internal systems to streamline operations, leads, and client workflows.', 'icon': 'layers',
         'img': 'images/services/erp.png'}
    ],

    'team': [
        {
            'name': 'Virat Verma',
            'role': 'Founder & CEO',
            'bio': 'Guides growth strategy, brand positioning, and high-level campaign planning.',
            'image': 'virat.jpg'
        },
        {
            'name': 'Zeba Heena',
            'role': 'Director',
            'bio': 'Leads consultations, client discovery, and campaign onboarding.',
            'image': 'zeba.jpg'
        },

        {
            'name': 'Richa Singh',
            'role': 'HR & Marketing',
            'bio': 'Handles talent acquisition, employee relations, and team culture.',
            'image': 'richa.jpg',
        },
        {
            'name': 'Babul Kumar',
            'role': 'Software Developer',
            'bio': 'Builds fast, conversion-focused websites and custom front-end experiences.',
            'image': 'babul.jpg'
        },
        {
            'name': 'Sahil',
            'role': 'SEO Specialist',
            'bio': 'Handles research, technical SEO, content planning, and reporting.',
            'image': 'sahil.jpg'
        }

    ],

    'packages': [
        {
            'id': 'standard_smo',
            'name': 'Standard SMO',
            'subtitle': 'Facebook + Instagram',
            'price': 250,
            'price_display': '$250 / 3 months',
            'features': ['20 creatives per month', '4 short videos', 'Captions and hashtags',
                         'Organic activity support', 'Basic ad management']
        },
        {
            'id': 'premium_smo',
            'name': 'Premium SMO',
            'subtitle': 'Facebook + Instagram + YouTube + X',
            'price': 310,
            'price_display': '$310 / 3 months',
            'features': ['20 creatives per month', '6 short videos', 'Enhanced posting schedule',
                         'Organic activity support', 'Paid ads coordination']
        },
        {
            'id': 'seo_package',
            'name': 'SEO Package',
            'subtitle': '20 target keywords',
            'price': 250,
            'price_display': '$250 / 3 months',
            'features': ['Keyword research', 'On-page SEO', 'Technical audits', 'Monthly reports', 'Competitor review']
        },
        {
            'id': 'combo_growth',
            'name': 'Combo Growth',
            'subtitle': 'SMO + SEO + Website + GMB',
            'price': 2100,
            'price_display': '$2100 / year',
            'features': ['Full-funnel strategy', 'Website refresh', 'SEO + SMM', 'Local visibility setup',
                         'Performance reporting']
        }
    ],

    'testimonials': [
        {'name': 'R. Jain',
         'text': 'Very smooth communication, timely delivery, and a clear improvement in our online visibility.'},
        {'name': 'Jatin Sharma',
         'text': 'The team was responsive and structured. We got our website and campaigns launched quickly.'},
        {'name': 'John',
         'text': 'Professional execution and strong design quality. Good option for service businesses.'}
    ],
    'faqs': [
        {
            'q': 'What services does Click Catcher offer?',
            'a': 'We offer website development, SEO, social media marketing, app development, graphic design, branding, brochure design, ERP solutions, CRM solutions, and digital growth services.'
        },
        {
            'q': 'How do I know which marketing service is right for my business?',
            'a': 'We first understand your business goals, target audience, and current digital presence, then suggest the most suitable service mix for growth.'
        },
        {
            'q': 'How long does it take to see results?',
            'a': 'The timeline depends on the service. Paid campaigns can show results quickly, while SEO and long-term organic growth usually take more time.'
        },
        {
            'q': 'Will I be able to track the performance of my campaigns?',
            'a': 'Yes, we provide reporting, analytics, and performance tracking so you can monitor results clearly.'
        },
        {
            'q': 'Why should I choose Click Catcher over other digital marketing agencies?',
            'a': 'We focus on strategy, quality execution, transparent communication, and measurable results tailored to your business needs.'
        }
    ]
}

BLOG_POSTS = [
    {
        "slug": "how-clickcatcher-drives-business-leads-using-digital-marketing",
        "title": "How ClickCatcher Drives Business Leads Using Digital Marketing",
        "author": "clickcatcher0@gmail.com",
        "date": "February 10, 2026",
        "category": "Blog",
        "comments": "0 Comments",
        "image": "images/blog1.jpg",
        "excerpt": "In today’s competitive digital ecosystem, generating consistent and high-quality business leads is one of the biggest challenges for brands. Many businesses invest heavily in online platforms but still struggle to...",
        "content": [
            "In today’s competitive digital ecosystem, generating consistent and high-quality business leads is one of the biggest challenges for brands. Many businesses invest heavily in online platforms but still struggle to convert visibility into actual business opportunities.",
            "At ClickCatcher, digital marketing is approached as a lead-generation engine, not just a branding activity. Every campaign is built around attracting the right audience, understanding search intent, and turning traffic into inquiries.",
            "SEO, paid campaigns, social media engagement, landing page optimization, and conversion-focused design all play a role in bringing better quality leads to a business.",
            "The real strength of a smart digital marketing system lies in combining content, trust, targeting, and performance tracking. This creates a more predictable flow of leads instead of random spikes in traffic.",
            "When businesses focus on relevance, consistency, and customer intent, digital marketing becomes more than promotion — it becomes a system for growth."
        ]
    },
    {
        "slug": "best-digital-marketing-company-in-noida-grow-your-business-online",
        "title": "Best Digital Marketing Company in Noida – Grow Your Business Online",
        "author": "clickcatcher0@gmail.com",
        "date": "January 22, 2026",
        "category": "Blog",
        "comments": "0 Comments",
        "image": "images/blog2.jpg",
        "excerpt": "In today’s competitive digital economy, simply having a business is not enough. Your brand needs visibility, credibility, and consistent engagement across digital platforms to survive and grow. Businesses in Noida...",
        "content": [
            "In today’s competitive digital economy, simply having a business is not enough. Your brand needs visibility, credibility, and consistent engagement across digital platforms to survive and grow.",
            "Businesses in Noida operate in a fast-moving market where customers compare options quickly and make decisions based on what they see online.",
            "A strong digital marketing company helps brands improve SEO, social media visibility, lead generation, ad performance, and website conversions.",
            "The right strategy combines local relevance with long-term online positioning. This includes Google visibility, audience targeting, strong creative assets, and a website experience that builds trust.",
            "Growing online is not about doing everything at once. It is about using the right channels with the right message at the right time."
        ]
    },
    {
        "slug": "clicks-intent-and-trust-the-new-rules-of-digital-marketing",
        "title": "Clicks, Intent, and Trust: The New Rules of Digital Marketing",
        "author": "clickcatcher0@gmail.com",
        "date": "December 31, 2025",
        "category": "Blog",
        "comments": "0 Comments",
        "image": "images/blog3.jpg",
        "excerpt": "Introduction Why Digital Marketing Needed a Reset Digital marketing has evolved far beyond impressions, likes, and surface-level engagement. Businesses today are no longer competing just for visibility; they are competing...",
        "content": [
            "Digital marketing has evolved far beyond impressions, likes, and surface-level engagement. Businesses today are no longer competing just for visibility; they are competing for relevance and trust.",
            "Clicks alone are no longer enough. What matters is whether the visitor has intent and whether your brand gives them enough confidence to take the next step.",
            "This is why modern marketing must focus on message clarity, audience intent, clean user experience, social proof, and conversion-driven content.",
            "Trust is built through consistent branding, transparent communication, useful content, and professional design.",
            "The brands that win online are not always the loudest. They are the ones that feel the most relevant and trustworthy."
        ]
    },
    {
        "slug": "which-digital-marketing-company-is-best-in-noida",
        "title": "Which Digital Marketing Company is Best in Noida?",
        "author": "clickcatcher0@gmail.com",
        "date": "December 20, 2025",
        "category": "Technology",
        "comments": "0 Comments",
        "image": "images/blog4.jpg",
        "excerpt": "In a fast-growing business hub like Noida, digital presence is no longer optional. Every brand, whether a startup, local business, or established enterprise, is competing for attention online. This intense...",
        "content": [
            "In a fast-growing business hub like Noida, digital presence is no longer optional. Every brand, whether a startup, local business, or established enterprise, is competing for attention online.",
            "Choosing the right digital marketing company depends on your goals, budget, industry, and expected outcomes.",
            "A strong agency should understand SEO, performance marketing, branding, lead generation, website optimization, and customer targeting.",
            "More importantly, it should focus on measurable results instead of vanity metrics.",
            "The best digital marketing partner is one that aligns strategy with business growth and adapts based on real performance data."
        ]
    },
    {
        "slug": "how-voice-search-is-driving-the-growth-of-aeo",
        "title": "How Voice Search is Driving the Growth of AEO",
        "author": "clickcatcher0@gmail.com",
        "date": "September 12, 2025",
        "category": "Technology",
        "comments": "0 Comments",
        "image": "images/blog5.jpg",
        "excerpt": "The way people search online is changing fast. With the rise of smart devices like Siri, Alexa, and Google Assistant, more and more users are relying on voice search instead...",
        "content": [
            "The way people search online is changing fast. With the rise of smart devices like Siri, Alexa, and Google Assistant, more users are relying on voice search instead of traditional typed queries.",
            "This shift is contributing to the growth of AEO, or Answer Engine Optimization, where content is designed to directly answer user questions.",
            "Voice search tends to be more conversational, more question-based, and often more local in intent.",
            "Businesses that optimize for direct answers, natural language, and structured content are better positioned for this new search behavior.",
            "As search continues to evolve, answer-focused content will become increasingly important for digital visibility."
        ]
    },
    {
        "slug": "how-to-fix-noindex-detected-errors-in-google-search-console",
        "title": "How to Fix “Noindex Detected” Errors in Google Search Console",
        "author": "clickcatcher0@gmail.com",
        "date": "July 25, 2025",
        "category": "Blog",
        "comments": "0 Comments",
        "image": "images/blog6.jpg",
        "excerpt": "As a website owner, SEO professional, or digital marketer, encountering a “Noindex Detected” error in Google Search Console can be frustrating. This error essentially means that Google has detected a...",
        "content": [
            "As a website owner, SEO professional, or digital marketer, encountering a 'Noindex Detected' error in Google Search Console can be frustrating.",
            "This usually means that Google has identified a page that contains a noindex directive, preventing it from appearing in search results.",
            "The first step is to inspect the affected page and confirm whether the noindex tag is intentional or accidental.",
            "You should also review robots directives, CMS settings, plugin behavior, and server-side page templates.",
            "Once corrected, request reindexing in Search Console and monitor the page until the issue is resolved."
        ]
    }
]


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            service TEXT,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def admin_required():
    return bool(session.get('admin_logged_in'))


@app.context_processor
def inject_site():
    return {'site': SITE}


@app.route('/')
def home():
    latest_blog_posts = BLOG_POSTS[:3]
    return render_template(
        'index.html',
        latest_blog_posts=latest_blog_posts
    )


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        service = request.form.get('service', '').strip()
        message = request.form.get('message', '').strip()

        if not name or not email or not message:
            flash('Please fill all required fields.', 'danger')
            return redirect(url_for('contact'))

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO contacts (name, email, phone, service, message) VALUES (?, ?, ?, ?, ?)',
            (name, email, phone, service, message)
        )
        conn.commit()
        conn.close()

        flash('Thanks! Your message has been submitted successfully.', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if email == ADMIN_EMAIL and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin_logged_in'] = True
            session['admin_email'] = email
            flash('Login successful.', 'success')
            return redirect(url_for('admin_dashboard'))

        flash('Please enter the correct email id and password.', 'danger')
        return redirect(url_for('admin_login'))

    return render_template('admin_login.html')


@app.route('/admin')
def admin_dashboard():
    if not admin_required():
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    contacts = conn.execute('SELECT * FROM contacts ORDER BY id DESC').fetchall()
    total_contacts = conn.execute('SELECT COUNT(*) AS total FROM contacts').fetchone()['total']
    conn.close()

    return render_template('admin.html', contacts=contacts, total_contacts=total_contacts)


@app.route('/admin/export')
def admin_export():
    if not admin_required():
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    rows = conn.execute(
        'SELECT id, name, email, phone, service, message, created_at FROM contacts ORDER BY id DESC'
    ).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Service', 'Message', 'Created At'])

    for row in rows:
        writer.writerow([
            row['id'],
            row['name'],
            row['email'],
            row['phone'],
            row['service'],
            row['message'],
            row['created_at']
        ])

    memory = io.BytesIO(output.getvalue().encode('utf-8'))
    memory.seek(0)

    return send_file(
        memory,
        mimetype='text/csv',
        as_attachment=True,
        download_name='contact_messages.csv'
    )


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin_login'))


# ---------------------------
# Existing service routes
# ---------------------------

@app.route('/facebook-marketing')
def facebook_marketing():
    return render_template('facebook_marketing.html')


@app.route('/instagram-marketing')
def instagram_marketing():
    return render_template('instagram_marketing.html')


@app.route('/linkedin-marketing')
def linkedin_marketing():
    return render_template('linkedin_marketing.html')


@app.route('/twitter-marketing')
def twitter_marketing():
    return render_template('twitter_marketing.html')


@app.route('/google-seo')
def google_seo():
    return render_template('google_seo.html')


@app.route('/gmb-seo')
def gmb_seo():
    return render_template('gmb_seo.html')


@app.route('/android-app-development')
def android_development():
    return render_template('android_development.html')


@app.route('/ios-app-development')
def ios_development():
    return render_template('ios_app_development.html')


@app.route('/ecommerce-website')
def ecommerce_website():
    return render_template('ecommerce_website.html')


@app.route('/dynamic-website')
def dynamic_website():
    return render_template('dynamic_website.html')


@app.route('/static-website')
def static_website():
    return render_template('static_website.html')


@app.route('/graphic-design-service')
def graphic_design_service():
    return render_template('graphic_design_service.html')


@app.route('/branding-logo-design')
def branding_logo_design():
    return render_template('branding_logo_design.html')


@app.route('/brochure-design')
def brochure_design():
    return render_template('brochure_design.html')


@app.route('/erp-services')
def erp_services():
    return render_template('erp_services.html')


@app.route('/crm-services')
def crm_services():
    return render_template('crm_services.html')


# ---------------------------
# Payment routes
# ---------------------------

@app.route('/pay-now')
def pay_now():
    plans = SITE['packages']
    return render_template(
        'pay_now.html',
        plans=plans,
        razorpay_key_id=RAZORPAY_KEY_ID
    )


@app.route('/create-order', methods=['POST'])
def create_order():
    data = request.get_json()
    plan_id = data.get("plan_id")

    selected_plan = next((plan for plan in SITE['packages'] if plan["id"] == plan_id), None)
    if not selected_plan:
        return jsonify({"error": "Invalid plan selected"}), 400

    amount_paise = int(selected_plan["price"]) * 100

    try:
        order = client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "receipt": f"receipt_{selected_plan['id']}",
            "notes": {
                "plan_name": selected_plan["name"]
            }
        })
    except Exception as e:
        return jsonify({"error": f"Razorpay error: {str(e)}"}), 500

    return jsonify({
        "order_id": order["id"],
        "amount": amount_paise,
        "plan_name": selected_plan["name"],
        "price": selected_plan["price"],
        "price_display": selected_plan["price_display"]
    })


@app.route('/payment-success', methods=['POST'])
def payment_success():
    razorpay_order_id = request.form.get('razorpay_order_id')
    razorpay_payment_id = request.form.get('razorpay_payment_id')
    razorpay_signature = request.form.get('razorpay_signature')

    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })

        return render_template(
            'payment_success.html',
            payment_id=razorpay_payment_id,
            order_id=razorpay_order_id
        )
    except Exception as e:
        return f"Payment verification failed: {str(e)}", 400


# ---------------------------
# Blog routes
# ---------------------------

@app.route('/blog')
def blog():
    recent_posts = BLOG_POSTS[:5]
    archives = ["February 2026", "January 2026", "December 2025", "September 2025", "July 2025"]
    categories = ["Blog", "Technology"]

    return render_template(
        'blog.html',
        blog_posts=BLOG_POSTS,
        recent_posts=recent_posts,
        archives=archives,
        categories=categories
    )


@app.route('/blog/<slug>')
def blog_post(slug):
    post = next((p for p in BLOG_POSTS if p["slug"] == slug), None)
    if not post:
        return "Post not found", 404

    recent_posts = BLOG_POSTS[:5]
    archives = ["February 2026", "January 2026", "December 2025", "September 2025", "July 2025"]
    categories = ["Blog", "Technology"]

    return render_template(
        'blog_post.html',
        post=post,
        recent_posts=recent_posts,
        archives=archives,
        categories=categories
    )


@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html', site=SITE)


@app.route('/terms-and-conditions')
def terms_and_conditions():
    return render_template('terms_and_conditions.html', site=SITE)


@app.route('/cancellation-refund-policy')
def cancellation_refund_policy():
    return render_template('cancellation_refund_policy.html', site=SITE)


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)
