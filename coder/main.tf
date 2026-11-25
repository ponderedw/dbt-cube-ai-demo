terraform {
  required_providers {
    coder = {
      source = "coder/coder"
    }
    docker = {
      source = "kreuzwerker/docker"
    }
  }
}

locals {
  username = data.coder_workspace_owner.me.name
  repo_url = "https://github.com/ponderedw/dbt-cube-ai-demo.git"
  repo_dir = "dbt-cube-ai-demo"
}

variable "docker_socket" {
  default     = ""
  description = "(Optional) Docker socket URI — leave empty to use the host default"
  type        = string
}

provider "docker" {
  host = var.docker_socket != "" ? var.docker_socket : null
}

# ─────────────────────────────────────────────────────────────────────────────
# Parameters
# ─────────────────────────────────────────────────────────────────────────────

data "coder_parameter" "aws_access_key_id" {
  name         = "aws_access_key_id"
  display_name = "AWS Access Key ID"
  description  = "AWS credentials for Bedrock LLM + embeddings"
  type         = "string"
  mutable      = true
  default      = ""
  order        = 1
  form_type    = "input"
  styling = jsonencode({
    mask_input = true
  })
}

data "coder_parameter" "aws_secret_access_key" {
  name         = "aws_secret_access_key"
  display_name = "AWS Secret Access Key"
  description  = "AWS credentials for Bedrock LLM + embeddings"
  type         = "string"
  mutable      = true
  default      = ""
  order        = 2
  form_type    = "input"
  styling = jsonencode({
    mask_input = true
  })
}

data "coder_parameter" "aws_region" {
  name         = "aws_region"
  display_name = "AWS Region"
  description  = "AWS region for Bedrock (e.g. us-east-1)"
  type         = "string"
  mutable      = true
  default      = "us-east-1"
  order        = 3
}

data "coder_parameter" "git_name" {
  name         = "git_name"
  display_name = "Git Name"
  description  = "Your full name for Git commits"
  type         = "string"
  mutable      = true
  default      = ""
  order        = 4
}

data "coder_parameter" "git_email" {
  name         = "git_email"
  display_name = "Git Email"
  description  = "Your email for Git commits"
  type         = "string"
  mutable      = true
  default      = ""
  order        = 5
}

# ─────────────────────────────────────────────────────────────────────────────
# Workspace data sources
# ─────────────────────────────────────────────────────────────────────────────

data "coder_provisioner" "me" {}
data "coder_workspace" "me" {}
data "coder_workspace_owner" "me" {}

# ─────────────────────────────────────────────────────────────────────────────
# Coder agent
# ─────────────────────────────────────────────────────────────────────────────

resource "coder_agent" "main" {
  arch = data.coder_provisioner.me.arch
  os   = "linux"

  metadata {
    display_name = "CPU Usage"
    key          = "0_cpu_usage"
    script       = "coder stat cpu"
    interval     = 10
    timeout      = 1
  }

  metadata {
    display_name = "RAM Usage"
    key          = "1_ram_usage"
    script       = "coder stat mem"
    interval     = 10
    timeout      = 1
  }

  startup_script = <<-EOT
    #!/bin/bash
    set -e

    if [ ! -f ~/.init_done ]; then
      cp -rT /etc/skel ~
      touch ~/.init_done
    fi

    # Base tools
    sudo apt-get update -q
    sudo apt-get install -y --fix-missing git curl wget ca-certificates gnupg software-properties-common

    # Install Docker Engine (DinD — isolated from host)
    if ! command -v docker &>/dev/null; then
      sudo install -m 0755 -d /etc/apt/keyrings
      curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
        | sudo gpg --dearmor --yes -o /etc/apt/keyrings/docker.gpg
      sudo chmod a+r /etc/apt/keyrings/docker.gpg
      sudo mkdir -p /etc/apt/sources.list.d
      VERSION_CODENAME=$(. /etc/os-release && echo "$VERSION_CODENAME")
      echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $VERSION_CODENAME stable" \
        | sudo tee /etc/apt/sources.list.d/docker.list
      sudo apt-get update -q
      sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
      sudo usermod -aG docker coder
    fi
    sudo service docker start

    # Install just (task runner)
    if ! command -v just &>/dev/null; then
      curl -fsSL https://just.systems/install.sh | sudo bash -s -- --to /usr/local/bin
    fi

    # Install dbt Fusion (dbt v2)
    mkdir -p "$HOME/.local/bin"
    export PATH="$HOME/.local/bin:$PATH"
    grep -q '\.local/bin' ~/.bashrc || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    if ! command -v dbt &>/dev/null || ! dbt --version 2>/dev/null | grep -q "2\."; then
      curl -fsSL https://public.cdn.getdbt.com/fs/install/install.sh | sh -s -- --update
    fi

    # Install code-server
    if ! command -v code-server &>/dev/null; then
      curl -fsSL https://code-server.dev/install.sh | sh -s -- --method standalone
    fi

    # Git config
    git config --global user.name "${data.coder_parameter.git_name.value != "" ? data.coder_parameter.git_name.value : data.coder_workspace_owner.me.name}"
    git config --global user.email "${data.coder_parameter.git_email.value != "" ? data.coder_parameter.git_email.value : data.coder_workspace_owner.me.email}"

    # Clone demo repo
    cd $HOME
    if [ -d "${local.repo_dir}/.git" ]; then
      git -C "${local.repo_dir}" pull || true
    else
      git clone ${local.repo_url} ${local.repo_dir}
    fi

    # dbt Fusion writes logs to <project>/logs/ — create it so non-root coder user can write
    mkdir -p $HOME/${local.repo_dir}/dbt/logs
    echo 'export DBT_PROFILES_DIR=$HOME/${local.repo_dir}/dbt' >> ~/.bashrc
    export DBT_PROFILES_DIR=$HOME/${local.repo_dir}/dbt

    # Write .env from parameters
    cat > $HOME/${local.repo_dir}/.env <<ENV
AWS_ACCESS_KEY_ID=${data.coder_parameter.aws_access_key_id.value}
AWS_SECRET_ACCESS_KEY=${data.coder_parameter.aws_secret_access_key.value}
AWS_REGION=${data.coder_parameter.aws_region.value}
LLM_MODEL_ID=bedrock:us.anthropic.claude-opus-4-7
EMBEDDING_MODEL=bedrock:amazon.titan-embed-text-v2:0
CUBEJS_API_SECRET=demo-secret-change-me
SUPERSET_SECRET_KEY=demo-superset-key
SECRET_KEY=demo-secret
FAST_API_ACCESS_SECRET_TOKEN=demo-token
STREAMLIT_PASSWORD=test
MILVUS_SERVER_URI=http://milvus:19530
CUBE_URL=http://cube_api:4000
CUBE_SQL_HOST=cube_api
CUBE_SQL_PORT=15432
CUBE_SQL_DATABASE=db
CUBE_SQL_USER=root
FASTAPI_URL=http://fastapi:8080
DEPLOY_ENV=local
ENV

    # Start VS Code
    code-server \
      --auth none \
      --port 13337 \
      --app-name "dbt-cube-ai-demo" \
      $HOME/${local.repo_dir} &

    # Start the full demo stack (via sg to pick up docker group)
    exec sg docker "cd $HOME/${local.repo_dir} && just all"
  EOT
}

# ─────────────────────────────────────────────────────────────────────────────
# Apps
# ─────────────────────────────────────────────────────────────────────────────

resource "coder_app" "code_server" {
  agent_id     = coder_agent.main.id
  slug         = "code-server"
  display_name = "VS Code"
  url          = "http://localhost:13337/?folder=/home/coder/${local.repo_dir}"
  icon         = "/icon/code.svg"
  subdomain    = false

  healthcheck {
    url       = "http://localhost:13337/healthz"
    interval  = 5
    threshold = 6
  }
}

resource "coder_app" "cube" {
  agent_id     = coder_agent.main.id
  slug         = "cube"
  display_name = "Cube Playground"
  url          = "http://localhost:4000"
  icon         = "/icon/cube.svg"
  subdomain    = true
  share        = "owner"
}

resource "coder_app" "superset" {
  agent_id     = coder_agent.main.id
  slug         = "superset"
  display_name = "Superset"
  url          = "http://localhost:8088"
  icon         = "/icon/superset.svg"
  subdomain    = true
  share        = "owner"
}

resource "coder_app" "chat" {
  agent_id     = coder_agent.main.id
  slug         = "chat"
  display_name = "AI Chat"
  url          = "http://localhost:8501"
  icon         = "/icon/streamlit.svg"
  subdomain    = true
  share        = "owner"
}

resource "coder_app" "dbt_docs" {
  agent_id     = coder_agent.main.id
  slug         = "dbt-docs"
  display_name = "dbt Docs"
  url          = "http://localhost:8082"
  icon         = "/icon/dbt.svg"
  subdomain    = true
  share        = "owner"
}

resource "coder_app" "milvus_ui" {
  agent_id     = coder_agent.main.id
  slug         = "milvus-ui"
  display_name = "Milvus UI"
  url          = "http://localhost:8003"
  icon         = "/icon/database.svg"
  subdomain    = true
  share        = "owner"
}

# ─────────────────────────────────────────────────────────────────────────────
# Docker resources
# ─────────────────────────────────────────────────────────────────────────────

resource "docker_image" "workspace" {
  name          = "codercom/enterprise-base:ubuntu"
  pull_triggers = ["codercom/enterprise-base:ubuntu"]
}

resource "docker_volume" "home" {
  name = "coder-${data.coder_workspace.me.id}-home"
  lifecycle { ignore_changes = all }
  labels {
    label = "coder.owner"
    value = data.coder_workspace_owner.me.name
  }
  labels {
    label = "coder.workspace_id"
    value = data.coder_workspace.me.id
  }
}

resource "docker_volume" "docker_data" {
  name = "coder-${data.coder_workspace.me.id}-docker-data"
  lifecycle { ignore_changes = all }
  labels {
    label = "coder.owner"
    value = data.coder_workspace_owner.me.name
  }
  labels {
    label = "coder.workspace_id"
    value = data.coder_workspace.me.id
  }
}

resource "docker_container" "workspace" {
  count    = data.coder_workspace.me.start_count
  image    = docker_image.workspace.name
  name     = "coder-${data.coder_workspace_owner.me.name}-${lower(data.coder_workspace.me.name)}"
  hostname = data.coder_workspace.me.name

  privileged = true

  entrypoint = [
    "sh", "-c",
    replace(coder_agent.main.init_script, "/localhost|127\\.0\\.0\\.1/", "host.docker.internal")
  ]

  env = ["CODER_AGENT_TOKEN=${coder_agent.main.token}"]

  host {
    host = "host.docker.internal"
    ip   = "host-gateway"
  }

  volumes {
    volume_name    = docker_volume.home.name
    container_path = "/home/coder"
    read_only      = false
  }

  volumes {
    volume_name    = docker_volume.docker_data.name
    container_path = "/var/lib/docker"
    read_only      = false
  }

  labels {
    label = "coder.owner"
    value = data.coder_workspace_owner.me.name
  }
  labels {
    label = "coder.workspace_id"
    value = data.coder_workspace.me.id
  }
}
