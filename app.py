from flask import Flask, render_template, request, redirect, url_for, session
from db import get_connection
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "secret_key_123"
TABLE_MAP = {'admin': 'admins', 'agent': 'agents', 'policyholder': 'policy_holders'}
ALLOWED_EXT = {'jpg', 'jpeg', 'png', 'webp'}

# Resolve paths relative to this file so they work from any working directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_BASE = os.path.join(BASE_DIR, 'static', 'uploads')

# Auto-create upload subdirectories on startup via os library
for _subdir in ('agents', 'policyholders'):
    os.makedirs(os.path.join(UPLOAD_BASE, _subdir), exist_ok=True)

# Validate uploaded file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

# ---------- Public Routes ----------


@app.route('/')
def home():
    return render_template("login.html")


@app.route('/login', methods=['GET'])
def login_page():
    return render_template("login.html")


# Handle login logic and session assignment based on role
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    role = request.form.get('role', '').strip()
    if not username or not password or not role:
        return render_template("login.html", error="All fields are required.")
    table = TABLE_MAP.get(role)
    if not table:
        return render_template("login.html", error="Invalid role selected.")
    conn = get_connection()
    if conn is None:
        return render_template("login.html", error="Database connection failed.")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            f"SELECT id, name, username FROM {table} WHERE username = %s AND password = %s AND is_active = 1", (username, password))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['user_id'] = user.get('id')
            session['username'] = user.get('name')
            session['login'] = user.get('username')
            session['role'] = role
            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif role == 'agent':
                return redirect(url_for('agent_dashboard'))
            else:
                return redirect(url_for('policyholder_dashboard'))
        else:
            return render_template("login.html", error="Invalid credentials or role.")
    except Exception as e:
        return render_template("login.html", error=f"An error occurred: {str(e)}")
    finally:
        conn.close()


# ---------- Admin Routes ----------
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('loggedin') or session.get('role') != 'admin':
        return redirect(url_for('login_page'))
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM policies WHERE status='active'")
        active_policies = cursor.fetchone()['cnt']
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM claims WHERE status IN ('submitted','under_review')")
        pending_claims = cursor.fetchone()['cnt']
        cursor.execute(
            "SELECT COALESCE(SUM(amount),0) AS total FROM premium_schedule WHERE status IN ('pending','overdue')")
        premiums_due = cursor.fetchone()['total']

        cursor.execute(
            "SELECT * FROM policy_types WHERE is_active=1 ORDER BY id")
        policy_types = cursor.fetchall()

        cursor.execute("""
            SELECT c.id, c.claim_number, ph.name AS holder_name,
                   p.policy_number, pt.name AS policy_type,
                   c.incident_date, c.amount_requested, c.status, c.submitted_at
            FROM claims c
            JOIN policy_holders ph ON c.submitted_by = ph.id
            JOIN policies p ON c.policy_id = p.id
            JOIN policy_types pt ON p.policy_type_id = pt.id
            ORDER BY c.submitted_at DESC
        """)
        claims = cursor.fetchall()

        cursor.execute("""
            SELECT ps.id, p.policy_number, ps.installment_number, ps.due_date,
                   ps.amount, ps.status, ps.paid_at, ph.name AS holder_name
            FROM premium_schedule ps
            JOIN policies p ON ps.policy_id = p.id
            JOIN policy_holders ph ON p.policyholder_id = ph.id
            ORDER BY ps.status DESC, ps.due_date ASC
        """)
        premiums = cursor.fetchall()

        cursor.execute("""
            SELECT ps.due_date, ps.amount, p.policy_number, ph.name AS holder_name,
                   DATEDIFF(CURDATE(), ps.due_date) AS days_overdue
            FROM premium_schedule ps
            JOIN policies p ON ps.policy_id = p.id
            JOIN policy_holders ph ON p.policyholder_id = ph.id
            WHERE ps.status = 'overdue'
            ORDER BY days_overdue DESC
        """)
        overdue = cursor.fetchall()

        cursor.execute("""
            SELECT pt.name, COUNT(*) AS cnt
            FROM policies p JOIN policy_types pt ON p.policy_type_id = pt.id
            WHERE p.status = 'active'
            GROUP BY pt.name
        """)
        breakdown = cursor.fetchall()

        cursor.execute("""
            SELECT ce.created_at, ce.event_type, ce.to_status, ce.note,
                   c.claim_number, c.amount_requested
            FROM claim_events ce
            JOIN claims c ON ce.claim_id = c.id
            ORDER BY ce.created_at DESC LIMIT 5
        """)
        recent_activity = cursor.fetchall()

        cursor.execute(
            "SELECT id, name, username FROM policy_holders WHERE is_active=1 ORDER BY name")
        all_policyholders = cursor.fetchall()

        cursor.execute(
            "SELECT id, name FROM agents WHERE is_active=1 ORDER BY name")
        all_agents = cursor.fetchall()

        # Fetch full agent/policyholder lists with pictures for People tab
        cursor.execute(
            "SELECT id, name, username, email, phone, commission_rate, is_active, picture FROM agents ORDER BY name")
        all_agents_full = cursor.fetchall()

        cursor.execute(
            "SELECT id, name, username, email, phone, is_active, picture FROM policy_holders ORDER BY name")
        all_policyholders_full = cursor.fetchall()

        cursor.execute("SELECT CURDATE() AS today")
        today = str(cursor.fetchone()['today'])

        # Fetch all policies with current agent info for agent assignment UI
        cursor.execute("""
            SELECT p.id, p.policy_number, ph.name AS policyholder_name, p.status,
                   p.agent_id, ag.name AS agent_name
            FROM policies p
            JOIN policy_holders ph ON p.policyholder_id = ph.id
            LEFT JOIN agents ag ON p.agent_id = ag.id
            ORDER BY ph.name, p.policy_number
        """)
        all_policies_assign = cursor.fetchall()

        return render_template("admin.html", active_policies=active_policies, pending_claims=pending_claims, premiums_due=premiums_due, policy_types=policy_types, claims=claims, premiums=premiums, overdue=overdue, breakdown=breakdown, recent_activity=recent_activity, all_policyholders=all_policyholders, all_agents=all_agents, all_agents_full=all_agents_full, all_policyholders_full=all_policyholders_full, all_policies_assign=all_policies_assign, today=today)
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()


# Upload profile picture for an agent or policyholder and store path in DB
@app.route('/admin/upload-picture', methods=['POST'])
def upload_picture():
    if not session.get('loggedin') or session.get('role') != 'admin':
        return redirect(url_for('login_page'))
    user_type = request.form.get('user_type')  # 'agent' or 'policyholder'
    user_id = request.form.get('user_id')
    file = request.files.get('picture')
    if not file or file.filename == '':
        return redirect(url_for('admin_dashboard'))
    if not allowed_file(file.filename):
        return "Invalid file type. Only jpg, png, webp allowed.", 400
    if len(file.read()) > 2 * 1024 * 1024:
        return "File too large. Max 2MB allowed.", 400
    file.seek(0)
    ext = file.filename.rsplit('.', 1)[1].lower()
    # Use UPLOAD_BASE (set at startup via os) — no hardcoded paths
    folder = os.path.join(UPLOAD_BASE, user_type + 's')
    filename = f"{user_id}.{ext}"
    save_path = os.path.join(folder, filename)
    file.save(save_path)
    db_path = f"uploads/{user_type}s/{filename}"
    table = 'agents' if user_type == 'agent' else 'policy_holders'
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE {table} SET picture=%s WHERE id=%s", (db_path, user_id))
        conn.commit()
        return redirect(url_for('admin_dashboard') + '#v-people')
    finally:
        conn.close()


# Create a new agent account (admin only)
@app.route('/admin/create-agent', methods=['POST'])
def create_agent():
    if not session.get('loggedin') or session.get('role') != 'admin':
        return redirect(url_for('login_page'))
    name = request.form.get('name', '').strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip() or None
    commission_rate = request.form.get('commission_rate', '5.00')
    if not name or not username or not password:
        return "Name, username and password are required.", 400
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO agents (name, username, password, phone, email, commission_rate)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, username, password, phone, email, commission_rate))
        conn.commit()
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        conn.rollback()
        return f"Error creating agent: {e}", 400
    finally:
        conn.close()


# Assign or change the agent on an existing policy (admin only)
@app.route('/admin/assign-agent', methods=['POST'])
def assign_agent():
    if not session.get('loggedin') or session.get('role') != 'admin':
        return redirect(url_for('login_page'))
    policy_id = request.form.get('policy_id')
    agent_id = request.form.get('agent_id') or None
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE policies SET agent_id=%s WHERE id=%s", (agent_id, policy_id))
        conn.commit()
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        conn.rollback()
        return f"Error assigning agent: {e}", 400
    finally:
        conn.close()


# Create a new policyholder account (admin only)
@app.route('/admin/create-policyholder', methods=['POST'])
def create_policyholder():
    if not session.get('loggedin') or session.get('role') != 'admin':
        return redirect(url_for('login_page'))
    name = request.form.get('name', '').strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip() or None
    date_of_birth = request.form.get('date_of_birth') or None
    address = request.form.get('address', '').strip() or None
    if not name or not username or not password:
        return "Name, username and password are required.", 400
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO policy_holders (name, username, password, phone, email, date_of_birth, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, username, password, phone, email, date_of_birth, address))
        conn.commit()
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        conn.rollback()
        return f"Error creating policyholder: {e}", 400
    finally:
        conn.close()


# Handle new policy type creation
@app.route('/admin/add-policy-type', methods=['POST'])
def admin_add_policy_type():
    if not session.get('loggedin') or session.get('role') != 'admin':
        return redirect(url_for('login_page'))
    name = request.form.get('name')
    coverage_category = request.form.get('coverage_category')
    base_annual_premium = request.form.get('base_annual_premium')
    max_coverage_amount = request.form.get('max_coverage_amount', 500000)
    min_term_years = request.form.get('min_term_years', 1)
    max_term_years = request.form.get('max_term_years', 30)
    grace_period_days = request.form.get('grace_period_days', 30)
    description = request.form.get('description', '')
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO policy_types (name, coverage_category, base_annual_premium, max_coverage_amount, min_term_years, max_term_years, grace_period_days, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                       (name, coverage_category, base_annual_premium, max_coverage_amount, min_term_years, max_term_years, grace_period_days, description))
        conn.commit()
        return redirect(url_for('admin_dashboard'))
    finally:
        conn.close()


# Issue a new policy and generate premium schedules
@app.route('/admin/issue-policy', methods=['POST'])
def admin_issue_policy():
    if not session.get('loggedin') or session.get('role') != 'admin':
        return redirect(url_for('login_page'))
    policyholder_id = request.form.get('policyholder_id')
    policy_type_id = request.form.get('policy_type_id')
    agent_id = request.form.get('agent_id') or None
    start_date = request.form.get('start_date')
    term_years = int(request.form.get('term_years', 1))
    annual_premium = request.form.get('annual_premium')
    sum_assured = request.form.get('sum_assured')
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS cnt FROM policies")
        count = cursor.fetchone()['cnt'] + 1
        policy_number = f"POL-{start_date[:4]}-{count:04d}"
        end_date = f"{int(start_date[:4]) + term_years}{start_date[4:]}"
        cursor.execute("""INSERT INTO policies (policy_number, policy_type_id, policyholder_id, agent_id, start_date, end_date, annual_premium, sum_assured, term_years) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) """,
                       (policy_number, policy_type_id, policyholder_id, agent_id, start_date, end_date, annual_premium, sum_assured, term_years))
        policy_id = cursor.lastrowid
        total_months = term_years * 12
        monthly_amount = round(float(annual_premium) / 12, 2)
        for i in range(1, total_months + 1):
            cursor.execute("""INSERT INTO premium_schedule (policy_id, installment_number, due_date, amount) VALUES (%s, %s, DATE_ADD(%s, INTERVAL %s MONTH), %s) """,
                           (policy_id, i, start_date, i, monthly_amount))
        conn.commit()
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        conn.rollback()
        return f"Error issuing policy: {e}"
    finally:
        conn.close()


# Mark a specific premium installment as paid
@app.route('/admin/collect-premium', methods=['POST'])
def collect_premium():
    if not session.get('loggedin') or session.get('role') != 'admin':
        return redirect(url_for('login_page'))
    installment_id = request.form.get('installment_id')
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE premium_schedule SET status='paid', paid_at=NOW() WHERE id=%s AND status != 'paid'", (installment_id,))
        conn.commit()
        return redirect(url_for('admin_dashboard'))
    finally:
        conn.close()


# ---------- Agent Routes ----------
@app.route('/agent/dashboard')
def agent_dashboard():
    if not session.get('loggedin') or session.get('role') != 'agent':
        return redirect(url_for('login_page'))
    agent_id = session['user_id']
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT COUNT(DISTINCT policyholder_id) AS cnt FROM policies WHERE agent_id=%s", (agent_id,))
        total_clients = cursor.fetchone()['cnt']
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM policies WHERE agent_id=%s AND status='active'", (agent_id,))
        active_managed = cursor.fetchone()['cnt']
        cursor.execute("""SELECT COALESCE(SUM(ps.amount * ag.commission_rate / 100), 0) AS earned FROM premium_schedule ps
        JOIN policies p ON ps.policy_id = p.id
        JOIN agents ag ON p.agent_id = ag.id
        WHERE p.agent_id = %s AND ps.status = 'paid' """, (agent_id,))
        commission_earned = cursor.fetchone()['earned']
        cursor.execute(
            "SELECT commission_rate FROM agents WHERE id=%s", (agent_id,))
        commission_rate = cursor.fetchone()['commission_rate']

        cursor.execute("""SELECT p.id, p.policy_number, ph.name AS client_name,
                   pt.name AS policy_type, p.start_date, p.end_date, p.annual_premium, p.status
            FROM policies p
            JOIN policy_holders ph ON p.policyholder_id = ph.id
            JOIN policy_types pt ON p.policy_type_id = pt.id
            WHERE p.agent_id = %s ORDER BY p.issued_at DESC """, (agent_id,))
        portfolio = cursor.fetchall()

        cursor.execute("""SELECT p.policy_number, ph.name AS client_name, p.annual_premium, ag.commission_rate,
                   ROUND(p.annual_premium * ag.commission_rate / 100, 2) AS total_commission,
                   COUNT(CASE WHEN ps.status='paid' THEN 1 END) AS paid_installments, COUNT(ps.id) AS total_installments,
                   ROUND(COALESCE(SUM(CASE WHEN ps.status='paid' THEN ps.amount END), 0) * ag.commission_rate / 100, 2) AS earned_to_date
            FROM policies p JOIN policy_holders ph ON p.policyholder_id = ph.id JOIN agents ag ON p.agent_id = ag.id
            LEFT JOIN premium_schedule ps ON ps.policy_id = p.id WHERE p.agent_id = %s
            GROUP BY p.id, p.policy_number, ph.name, p.annual_premium, ag.commission_rate """, (agent_id,))
        commissions = cursor.fetchall()

        cursor.execute(
            "SELECT * FROM policy_types WHERE is_active=1 ORDER BY id")
        policy_types = cursor.fetchall()

        cursor.execute(
            "SELECT id, name FROM policy_holders WHERE is_active=1 ORDER BY name")
        all_policyholders = cursor.fetchall()
        return render_template("agent.html", total_clients=total_clients, active_managed=active_managed, commission_earned=commission_earned, commission_rate=commission_rate, portfolio=portfolio, commissions=commissions, policy_types=policy_types, all_policyholders=all_policyholders)
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()


# Allow agents to submit policies on behalf of clients
@app.route('/agent/submit-policy', methods=['POST'])
def agent_submit_policy():
    if not session.get('loggedin') or session.get('role') != 'agent':
        return redirect(url_for('login_page'))
    agent_id = session['user_id']
    policyholder_id = request.form.get('policyholder_id')
    policy_type_id = request.form.get('policy_type_id')
    start_date = request.form.get('start_date')
    term_years = int(request.form.get('term_years', 1))
    annual_premium = request.form.get('annual_premium')
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS cnt FROM policies")
        count = cursor.fetchone()['cnt'] + 1
        policy_number = f"POL-{start_date[:4]}-{count:04d}"
        end_date = f"{int(start_date[:4]) + term_years}{start_date[4:]}"
        cursor.execute("""INSERT INTO policies (policy_number, policy_type_id, policyholder_id, agent_id, start_date, end_date, annual_premium) VALUES (%s, %s, %s, %s, %s, %s, %s) """,
                       (policy_number, policy_type_id, policyholder_id, agent_id, start_date, end_date, annual_premium))
        policy_id = cursor.lastrowid

        total_months = term_years * 12
        monthly_amount = round(float(annual_premium) / 12, 2)
        for i in range(1, total_months + 1):
            cursor.execute("""INSERT INTO premium_schedule (policy_id, installment_number, due_date, amount) VALUES (%s, %s, DATE_ADD(%s, INTERVAL %s MONTH), %s) """,
                           (policy_id, i, start_date, i, monthly_amount))
        conn.commit()
        return redirect(url_for('agent_dashboard'))
    except Exception as e:
        conn.rollback()
        return f"Error: {e}"
    finally:
        conn.close()


# ---------- Policyholder Routes ----------
@app.route('/policyholder/dashboard')
def policyholder_dashboard():
    if not session.get('loggedin') or session.get('role') != 'policyholder':
        return redirect(url_for('login_page'))
    user_id = session['user_id']
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""SELECT p.id, p.policy_number, pt.name AS policy_type, p.start_date, p.end_date, p.annual_premium, p.status
            FROM policies p JOIN policy_types pt ON p.policy_type_id = pt.id WHERE p.policyholder_id = %s ORDER BY p.issued_at DESC """, (user_id,))
        policies = cursor.fetchall()

        cursor.execute("""SELECT c.id, c.claim_number, p.policy_number, c.incident_date, c.amount_requested,
                   COALESCE(c.approved_amount, 0) AS amount_approved, c.status, c.submitted_at FROM claims c
            JOIN policies p ON c.policy_id = p.id WHERE c.submitted_by = %s
            ORDER BY c.submitted_at DESC """, (user_id,))
        claims = cursor.fetchall()

        cursor.execute("""SELECT ps.id, ps.due_date, ps.amount, p.policy_number FROM premium_schedule ps
            JOIN policies p ON ps.policy_id = p.id WHERE p.policyholder_id = %s AND ps.status IN ('pending','overdue')
            ORDER BY ps.due_date ASC LIMIT 1 """, (user_id,))
        next_installment = cursor.fetchone()

        cursor.execute("""SELECT p.id, p.policy_number, pt.name AS policy_type,
                   MAX(CASE WHEN ps.status='overdue' AND DATEDIFF(CURDATE(), ps.due_date) > 30 THEN 1 ELSE 0 END) AS is_blocked
            FROM policies p JOIN policy_types pt ON p.policy_type_id = pt.id
            LEFT JOIN premium_schedule ps ON ps.policy_id = p.id WHERE p.policyholder_id = %s AND p.status = 'active'
            GROUP BY p.id, p.policy_number, pt.name """, (user_id,))
        active_policies = cursor.fetchall()

        cursor.execute("""SELECT p.policy_number, pt.name AS policy_type, p.status FROM policies p JOIN policy_types pt ON p.policy_type_id = pt.id
            WHERE p.policyholder_id = %s AND p.status = 'active' """, (user_id,))
        coverage_summary = cursor.fetchall()

        cursor.execute("""SELECT c.claim_number, c.status, c.submitted_at, p.policy_number FROM claims c JOIN policies p ON c.policy_id = p.id
            WHERE c.submitted_by = %s ORDER BY c.submitted_at DESC LIMIT 1 """, (user_id,))
        latest_claim = cursor.fetchone()
        return render_template("policy-holder.html", policies=policies, claims=claims, next_installment=next_installment, active_policies=active_policies, coverage_summary=coverage_summary, latest_claim=latest_claim)
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()


# Submit a new claim — validate incident_date is not future-dated
@app.route('/policyholder/submit-claim', methods=['POST'])
def submit_claim():
    if not session.get('loggedin') or session.get('role') != 'policyholder':
        return redirect(url_for('login_page'))
    user_id = session['user_id']
    policy_id = request.form.get('policy_id')
    incident_date = request.form.get('incident_date')
    amount_requested = request.form.get('amount_requested')
    description = request.form.get('description')
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT CURDATE() AS today")
        today = str(cursor.fetchone()['today'])
        if incident_date > today:
            return "Incident date cannot be in the future.", 400
        cursor.execute("""
            SELECT start_date FROM policies WHERE id = %s AND policyholder_id = %s
        """, (policy_id, user_id))
        pol = cursor.fetchone()
        if not pol:
            return "Policy not found or access denied.", 403
        if incident_date < str(pol['start_date']):
            return "Incident date cannot be before the policy effective date.", 400
        cursor.execute("SELECT COUNT(*) AS cnt FROM claims")
        count = cursor.fetchone()['cnt'] + 1
        claim_number = f"CLM-{incident_date[:4]}-{count:04d}"
        cursor.execute("""INSERT INTO claims (claim_number, policy_id, submitted_by, incident_date, description, amount_requested)
            VALUES (%s, %s, %s, %s, %s, %s) """, (claim_number, policy_id, user_id, incident_date, description, amount_requested))
        claim_id = cursor.lastrowid
        cursor.execute("""INSERT INTO claim_events (claim_id, event_type, to_status, note, actor_id, actor_role)
            VALUES (%s, 'status_change', 'submitted', %s, %s, 'policyholder') """, (claim_id, f"Claim submitted by {session['username']}", user_id))
        conn.commit()
        return redirect(url_for('policyholder_dashboard'))
    except Exception as e:
        conn.rollback()
        return f"Error: {e}"
    finally:
        conn.close()


# ---------- Shared Policy Detail Route ----------
@app.route('/policy-detail')
def policy_detail():
    if not session.get('loggedin'):
        return redirect(url_for('login_page'))
    policy_id = request.args.get('id')
    if not policy_id:
        return redirect(url_for('login_page'))
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""SELECT p.*, pt.name AS policy_type, pt.coverage_category, pt.description AS type_description,
                   ph.name AS holder_name, ag.name AS agent_name FROM policies p
            JOIN policy_types pt ON p.policy_type_id = pt.id JOIN policy_holders ph ON p.policyholder_id = ph.id
            LEFT JOIN agents ag ON p.agent_id = ag.id WHERE p.id = %s """, (policy_id,))
        policy = cursor.fetchone()
        if not policy:
            return "Policy not found.", 404
        if session['role'] == 'policyholder' and policy.get('policyholder_id') != session['user_id']:
            return redirect(url_for('policyholder_dashboard'))
        cursor.execute(
            "SELECT * FROM premium_schedule WHERE policy_id = %s ORDER BY installment_number", (policy_id,))
        installments = cursor.fetchall()
        cursor.execute("""SELECT c.id, c.claim_number, c.incident_date, c.amount_requested,
                   COALESCE(c.approved_amount, 0) AS amount_approved, c.status FROM claims c
            WHERE c.policy_id = %s ORDER BY c.submitted_at DESC """, (policy_id,))
        claims = cursor.fetchall()
        cursor.execute(
            "SELECT * FROM nominations WHERE policy_id = %s ORDER BY id", (policy_id,))
        nominations = cursor.fetchall()
        return render_template("policy-detail.html", policy=policy, installments=installments, claims=claims, nominations=nominations)
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()


# Mark installment paid — verify it belongs to the requesting policyholder
@app.route('/policy/pay-installment', methods=['POST'])
def pay_installment():
    if not session.get('loggedin'):
        return redirect(url_for('login_page'))
    installment_id = request.form.get('installment_id')
    policy_id = request.form.get('policy_id')
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        if session.get('role') == 'policyholder':
            cursor.execute("""
                SELECT ps.id FROM premium_schedule ps
                JOIN policies p ON ps.policy_id = p.id
                WHERE ps.id = %s AND p.id = %s AND p.policyholder_id = %s
            """, (installment_id, policy_id, session['user_id']))
            if not cursor.fetchone():
                return "Unauthorized: installment does not belong to your policy.", 403
        cursor.execute(
            "UPDATE premium_schedule SET status='paid', paid_at=NOW() WHERE id=%s AND status != 'paid'", (installment_id,))
        conn.commit()
        return redirect(url_for('policy_detail', id=policy_id))
    finally:
        conn.close()


# ---------- Adjudication Routes ----------
@app.route('/adjudicate')
def adjudicate():
    if not session.get('loggedin') or session.get('role') not in ('admin', 'agent'):
        return redirect(url_for('login_page'))
    claim_id = request.args.get('id')
    if not claim_id:
        return redirect(url_for('admin_dashboard'))
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""SELECT c.*, ph.name AS holder_name, p.policy_number, pt.name AS policy_type,
                   COALESCE(pay.amount_approved, 0) AS amount_approved FROM claims c
            JOIN policy_holders ph ON c.submitted_by = ph.id JOIN policies p ON c.policy_id = p.id
            JOIN policy_types pt ON p.policy_type_id = pt.id LEFT JOIN payouts pay ON pay.claim_id = c.id WHERE c.id = %s """, (claim_id,))
        claim = cursor.fetchone()
        if not claim:
            return "Claim not found.", 404
        cursor.execute("""SELECT ce.*, COALESCE(ph.name, ag.name, ad.name) AS actor_name FROM claim_events ce
            LEFT JOIN policy_holders ph ON ce.actor_id = ph.id AND ce.actor_role = 'policyholder'
            LEFT JOIN agents ag ON ce.actor_id = ag.id AND ce.actor_role = 'agent'
            LEFT JOIN admins ad ON ce.actor_id = ad.id AND ce.actor_role = 'admin'
            WHERE ce.claim_id = %s ORDER BY ce.created_at ASC """, (claim_id,))
        events = cursor.fetchall()
        return render_template("adjudicate.html", claim=claim, events=events)
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()


# Handle claim status transitions — guard finalized claims from re-adjudication
@app.route('/adjudicate/save', methods=['POST'])
def adjudicate_save():
    if not session.get('loggedin') or session.get('role') not in ('admin', 'agent'):
        return redirect(url_for('login_page'))
    claim_id = request.form.get('claim_id')
    action = request.form.get('action')
    note = request.form.get('note')
    approved_amount = request.form.get('approved_amount')
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT status FROM claims WHERE id=%s", (claim_id,))
        row = cursor.fetchone()
        if not row:
            return "Claim not found.", 404
        old_status = row['status']
        if old_status in ('approved', 'rejected', 'paid'):
            return "This claim is already finalized and cannot be re-adjudicated.", 400
        valid_transitions = {
            'submitted': ('under_review', 'approved', 'rejected'),
            'under_review': ('approved', 'rejected'),
            'approved': ('paid',)
        }
        if action not in valid_transitions.get(old_status, ()):
            return f"Invalid transition: {old_status} → {action}.", 400
        cursor.execute("UPDATE claims SET status=%s WHERE id=%s",
                       (action, claim_id))
        if action in ('approved', 'rejected', 'paid'):
            cursor.execute(
                "UPDATE claims SET closed_at=NOW() WHERE id=%s", (claim_id,))
        cursor.execute("""INSERT INTO claim_events (claim_id, event_type, from_status, to_status, note, actor_id, actor_role)
            VALUES (%s, 'status_change', %s, %s, %s, %s, %s) """,
                       (claim_id, old_status, action, note, session['user_id'], session['role']))
        if action == 'approved' and approved_amount:
            cursor.execute(
                "SELECT id FROM payouts WHERE claim_id=%s", (claim_id,))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO payouts (claim_id, amount_approved, payout_date) VALUES (%s, %s, CURDATE())", (claim_id, approved_amount))
            cursor.execute(
                "UPDATE claims SET approved_amount=%s WHERE id=%s", (approved_amount, claim_id))
        if action == 'paid':
            cursor.execute(
                "UPDATE payouts SET payout_date=CURDATE() WHERE claim_id=%s", (claim_id,))
        conn.commit()
        return redirect(url_for('adjudicate', id=claim_id))
    except Exception as e:
        conn.rollback()
        return f"Error: {e}"
    finally:
        conn.close()

# Clear user session on logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))


if __name__ == "__main__":
    app.run(debug=True)
