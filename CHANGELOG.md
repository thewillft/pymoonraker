# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project scaffold
- Async `MoonrakerClient` with WebSocket JSON-RPC and HTTP transports
- Synchronous `SyncMoonrakerClient` wrapper
- Pydantic v2 models for printer objects, server info, jobs, files
- Event dispatch system with 25+ typed notification events
- Authentication support (API key, JWT, oneshot tokens)
- Auto-reconnect with exponential backoff
- YAML API schema (`schema/moonraker_api.yaml`) with 12 namespaces and 60+ methods
- Code generation script (`scripts/generate_bindings.py`)
- Auto-generated typed API bindings
- File upload/download via HTTP transport
- GitHub Actions CI (lint, typecheck, test matrix, codegen freshness)
- PyPI publish workflow
- Full test suite (30 tests)
