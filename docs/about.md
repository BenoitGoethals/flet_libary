# About Library Manager

## Overview

Library Manager is a modern, cross-platform library management application designed to streamline book cataloging,
client management, and rental tracking. Built with Flet and SQLAlchemy, it provides a responsive user interface that
works seamlessly across desktop and web platforms.

## Project Information

- **Project Name**: Flet Library Manager
- **Version**: 0.1.0
- **License**: Copyright (C) 2023-2026 by Flet
- **Repository**: [github.com/BenoitGoethals/flet_libary](https://github.com/BenoitGoethals/flet_libary)
- **Documentation**: [benoitgoethals.github.io/flet_libary](https://benoitgoethals.github.io/flet_libary/)

## Key Features

### Core Functionality

- **Comprehensive Book Management**: Add, edit, search, and delete books with detailed metadata and storage assignment
- **Client Tracking**: Manage library members with complete rental history
- **Rental System**: Full lifecycle management including checkout, returns, due dates, and overdue tracking
- **Storage Organization**: Physical location management for efficient book organization
- **Dashboard Analytics**: Real-time statistics and active rental overview

### Technical Features

- **Role-Based Access Control**: Secure authentication with admin and user roles
- **Multi-Database Support**: Compatible with SQLite, MSSQL, and MariaDB
- **Email Notifications**: Automated reminders for due and overdue rentals via SMTP
- **Async Architecture**: High-performance asynchronous operations with SQLAlchemy
- **Cross-Platform**: Runs on Windows, macOS, Linux, and web browsers

## Technology Stack

### Frontend

- **Flet (0.83.0+)**: Flutter-based Python UI framework for cross-platform development
- **Material Design**: Modern, responsive UI components

### Backend

- **SQLAlchemy (2.0.48+)**: Async ORM for database operations
- **aiosqlite (0.22.1+)**: Async SQLite adapter
- **Python 3.10+**: Core programming language

### Configuration & Data

- **YAML**: Application configuration (`settings.yml`)
- **SQLite/MSSQL/MariaDB**: Flexible database backend support

### Development & Testing

- **pytest (9.0.2+)**: Testing framework
- **pytest-asyncio (1.3.0+)**: Async test support
- **MkDocs Material**: Documentation generation

## Development Setup

### Prerequisites

- Python 3.10 or higher
- UV package manager (configured for this project)

### Installation
