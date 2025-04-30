# PostgreSQL Docker Compose Stack with pgAdmin and MCP Toolbox Integration

![MCP Toolbox for Databases](https://storage.googleapis.com/gweb-cloudblog-publish/images/MCP_Toolbox_for_Databases_-ADK.max-2200x2200.jpg)

## Overview

This repository contains a Docker Compose setup to quickly spin up a PostgreSQL database environment with the following components:

- PostgreSQL database with a sample table
- pgAdmin 4 web-based administration tool
- Integration with MCP Toolbox for database management
- Pre-configured environment for easy development and testing
- Sample Python agent application (requires Google ADK)

## Prerequisites

- Docker installed ([Installation Guide](https://docs.docker.com/get-docker/))
- Docker Compose installed ([Installation Guide](https://docs.docker.com/compose/install/))
- Node.js (v14+) with npm/npx ([Installation Guide](https://nodejs.org/))
- Python 3.9+ and pip ([Python Installation](https://www.python.org/downloads/))
- Google Agent Development Kit (ADK) ([Installation Guide](https://google.github.io/adk-docs/get-started/installation/))

## Getting Started

Extract the files of this folder and run docker compose:  
_docker compose up -d_

## Using the MCP Inspector:

Run the following command:   
_npx @modelcontextprotocol/inspector_