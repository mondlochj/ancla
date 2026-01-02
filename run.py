#!/usr/bin/env python3
"""
Ancla Capital - Lending Platform
Entry point for the Flask application
"""
import os
import click
from app import create_app
from app.extensions import db
from app.models.user import User, Role, RoleName
from app.models.loan import LoanProduct

app = create_app()


@app.cli.command('init-db')
def init_db():
    """Initialize the database with tables and seed data."""
    click.echo('Creating database tables...')
    db.create_all()

    click.echo('Inserting default roles...')
    Role.insert_roles()

    click.echo('Inserting default loan products...')
    LoanProduct.insert_default_products()

    click.echo('Database initialized successfully!')


@app.cli.command('create-admin')
@click.argument('email')
@click.argument('password')
def create_admin(email, password):
    """Create an admin user."""
    admin_role = Role.query.filter_by(name=RoleName.ADMIN.value).first()
    if not admin_role:
        click.echo('Error: Roles not initialized. Run init-db first.')
        return

    existing = User.query.filter_by(email=email.lower()).first()
    if existing:
        click.echo(f'Error: User with email {email} already exists.')
        return

    user = User(
        email=email.lower(),
        first_name='Admin',
        last_name='User',
        role_id=admin_role.id,
        is_verified=True,
        is_active=True
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    click.echo(f'Admin user {email} created successfully!')


@app.cli.command('create-user')
@click.argument('email')
@click.argument('password')
@click.argument('role')
def create_user(email, password, role):
    """Create a user with specified role."""
    role_obj = Role.query.filter_by(name=role).first()
    if not role_obj:
        click.echo(f'Error: Role {role} not found.')
        click.echo(f'Available roles: {", ".join([r.name for r in Role.query.all()])}')
        return

    existing = User.query.filter_by(email=email.lower()).first()
    if existing:
        click.echo(f'Error: User with email {email} already exists.')
        return

    user = User(
        email=email.lower(),
        first_name=role,
        last_name='User',
        role_id=role_obj.id,
        is_verified=True,
        is_active=True
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    click.echo(f'User {email} with role {role} created successfully!')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
