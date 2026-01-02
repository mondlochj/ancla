from datetime import datetime
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from .forms import (LoginForm, RegistrationForm, ForgotPasswordForm,
                    ResetPasswordForm, ChangePasswordForm)
from ...models.user import User, Role, RoleName
from ...models.borrower import Borrower
from ...extensions import db
from ...services.email import send_verification_email
from ...services.audit_service import log_user_action


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'danger')
                return redirect(url_for('auth.login'))

            if not user.is_verified:
                flash('Please verify your email address before logging in.', 'warning')
                return redirect(url_for('auth.unverified'))

            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()

            log_user_action(user, 'login')

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            # Redirect based on role
            if user.role.name == RoleName.BORROWER.value:
                return redirect(url_for('loans.my_loans'))
            return redirect(url_for('admin.dashboard'))

        flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Get or create borrower role
        borrower_role = Role.query.filter_by(name=RoleName.BORROWER.value).first()
        if not borrower_role:
            flash('System error. Please try again later.', 'danger')
            return redirect(url_for('auth.register'))

        user = User(
            email=form.email.data.lower(),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role_id=borrower_role.id,
            is_verified=False
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        # Check if there's a borrower with this email and auto-link
        borrower = Borrower.query.filter(
            Borrower.email.ilike(form.email.data),
            Borrower.user_id.is_(None)
        ).first()
        if borrower:
            borrower.user_id = user.id
            db.session.commit()
            flash('Your account has been linked to your borrower profile.', 'info')

        # Send verification email
        if send_verification_email(user):
            flash('Registration successful! Please check your email to verify your account.', 'success')
        else:
            flash('Registration successful but verification email could not be sent. Please contact support.', 'warning')

        log_user_action(user, 'register')

        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/verify/<token>')
def verify_email(token):
    if current_user.is_authenticated and current_user.is_verified:
        return redirect(url_for('admin.dashboard'))

    user = User.verify_token(token)
    if user is None:
        flash('The verification link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))

    if user.is_verified:
        flash('Your email has already been verified.', 'info')
        return redirect(url_for('auth.login'))

    user.is_verified = True
    user.verification_token = None
    user.token_expires = None
    db.session.commit()

    log_user_action(user, 'email_verified')

    flash('Your email has been verified! You can now log in.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/unverified')
def unverified():
    if current_user.is_authenticated and current_user.is_verified:
        return redirect(url_for('admin.dashboard'))
    return render_template('auth/unverified.html')


@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    email = request.form.get('email')
    if not email:
        flash('Please provide your email address.', 'warning')
        return redirect(url_for('auth.unverified'))

    user = User.query.filter_by(email=email.lower()).first()
    if user and not user.is_verified:
        if send_verification_email(user):
            db.session.commit()
            flash('Verification email sent! Please check your inbox.', 'success')
        else:
            flash('Could not send verification email. Please try again later.', 'danger')
    else:
        # Don't reveal if user exists
        flash('If an account exists with that email, a verification link has been sent.', 'info')

    return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
@login_required
def logout():
    log_user_action(current_user, 'logout')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            log_user_action(current_user, 'password_changed')
            flash('Your password has been changed.', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Current password is incorrect.', 'danger')

    return render_template('auth/change_password.html', form=form)


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            # Generate reset token and send email
            # For now, just show a message
            pass
        # Always show success to prevent email enumeration
        flash('If an account exists with that email, password reset instructions have been sent.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html', form=form)
