#!/usr/bin/env python3
"""Self-check of the scientific-writing environment in Oh My Pi, without a model call.

Run through the launcher (``scripts/omp-science --check``) or directly from the
repository root. It checks what the environment promises:

1. settings in the profile with the science overlay: foreign discovery providers
   off, no *model* provider disabled, ``modelRoleStorage: project``, advisor off,
   every ``@role`` used by an agent defined;
2. credentials borrowed from the default profile: the profile's ``models.yml`` matches
   ``.omp/science/models.yml``, and ``omp token`` resolves each provider through it
   (exit status only; the token is discarded);
3. the composed session over RPC (``get_state``, ``get_available_commands``): sticky
   rules and science context present, every skill, command and agent under ``.omp/``
   discovered, and nothing named after a skill/agent/command from another harness
   (``~/.claude``, ``~/.codex``, ``~/.agents``, ...) leaking in.

Exit 1 on any FAIL. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import queue
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

MODEL_PROVIDERS = {"anthropic", "openai", "openai-codex", "google", "opencode-go", "openrouter"}
FOREIGN_DISCOVERY = {"claude", "claude-md", "codex", "gemini", "opencode", "agents", "github"}
MODEL_PROVIDERS_NEEDED = ("anthropic", "openai-codex")


class Report:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str]] = []

    def check(self, ok: bool, name: str, detail: str = "") -> None:
        self.rows.append(("PASS" if ok else "FAIL", name, detail))

    def warn(self, name: str, detail: str) -> None:
        self.rows.append(("WARN", name, detail))

    @property
    def failed(self) -> bool:
        return any(status == "FAIL" for status, _, _ in self.rows)


def omp(profile: str, *args: str, timeout: float = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["omp", "--profile", profile, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        env=os.environ,
    )


def setting(profile: str, key: str) -> object:
    result = omp(profile, "config", "get", key, "--json")
    if result.returncode != 0:
        return None
    return json.loads(result.stdout).get("value")


def expected_names(root: Path) -> dict[str, set[str]]:
    omp_dir = root / ".omp"
    return {
        "skills": {p.parent.name for p in omp_dir.glob("skills/*/SKILL.md")},
        "commands": {p.stem for p in omp_dir.glob("commands/*.md")},
        "agents": {p.stem for p in omp_dir.glob("agents/*.md")},
    }


def foreign_names(root: Path) -> set[str]:
    """Names of skills, agents and commands other harnesses keep on this machine."""
    home = Path.home()
    bases = [
        home / ".claude",
        home / ".codex",
        home / ".agents",
        home / ".agent",
        home / ".gemini",
        home / ".config" / "opencode",
        root / ".claude",
        root / ".github",
    ]
    names: set[str] = set()
    for base in bases:
        for sub in ("skills", "agents", "commands"):
            directory = base / sub
            if not directory.is_dir():
                continue
            for entry in directory.iterdir():
                if entry.name.startswith("."):
                    continue
                names.add(entry.stem if entry.suffix == ".md" else entry.name)
    return names


def rpc_session(profile: str, context: Path, timeout: float) -> tuple[dict, list[dict], str]:
    """Start `omp --mode rpc`, ask for state and commands, and stop it."""
    process = subprocess.Popen(
        [
            "omp",
            "--profile",
            profile,
            "--mode",
            "rpc",
            "--no-session",
            "--no-title",
            "--append-system-prompt",
            str(context),
            "--model",
            "@writer",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=os.environ,
    )
    lines: queue.Queue[str] = queue.Queue()
    threading.Thread(
        target=lambda: [lines.put(line) for line in process.stdout], daemon=True
    ).start()
    errors: list[str] = []
    threading.Thread(target=lambda: errors.extend(process.stderr), daemon=True).start()

    def wait_for(predicate) -> dict | None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                raw = lines.get(timeout=0.5)
            except queue.Empty:
                if process.poll() is not None:
                    return None
                continue
            try:
                frame = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if predicate(frame):
                return frame
        return None

    try:
        if wait_for(lambda f: f.get("type") == "ready") is None:
            return {}, [], "".join(errors)[-2000:]
        assert process.stdin is not None
        process.stdin.write(json.dumps({"id": "state", "type": "get_state"}) + "\n")
        process.stdin.write(json.dumps({"id": "cmds", "type": "get_available_commands"}) + "\n")
        process.stdin.flush()
        state = wait_for(lambda f: f.get("id") == "state") or {}
        commands = wait_for(lambda f: f.get("id") == "cmds") or {}
        return (
            state.get("data") or {},
            (commands.get("data") or {}).get("commands", []),
            "".join(errors)[-2000:],
        )
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--profile", default="scientific-writing")
    parser.add_argument("--timeout", type=float, default=90)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    os.chdir(root)
    overlay = root / ".omp" / "science" / "overlay.yml"
    context = root / ".omp" / "science" / "CONTEXT.md"
    os.environ["PI_CONFIG_FILES"] = str(overlay)
    report = Report()
    expected = expected_names(root)

    # 1. Settings.
    disabled = set(setting(args.profile, "disabledProviders") or [])
    report.check(
        FOREIGN_DISCOVERY <= disabled, "descoberta estrangeira desligada", str(sorted(disabled))
    )
    report.check(
        not (disabled & MODEL_PROVIDERS),
        "nenhum provedor de modelo desligado",
        str(sorted(disabled & MODEL_PROVIDERS)),
    )
    enabled = setting(args.profile, "enabledProviders") or []
    report.check(enabled == [], "enabledProviders vazio", str(enabled))
    storage = setting(args.profile, "modelRoleStorage")
    report.check(storage == "project", "modelRoleStorage = project", str(storage))
    advisor = setting(args.profile, "advisor.enabled")
    report.check(advisor is False, "advisor desligado", str(advisor))
    roles = setting(args.profile, "modelRoles") or {}
    used = set()
    for agent in (root / ".omp" / "agents").glob("*.md"):
        used.update(re.findall(r'^model:\s*"?@(\w+)', agent.read_text(encoding="utf-8"), re.M))
    missing_roles = sorted(role for role in used if role not in roles)
    report.check(not missing_roles, "papéis dos agentes definidos", f"faltando: {missing_roles}")

    # 2. Credentials, borrowed from the default profile through the profile's models.yml.
    models_src = root / ".omp" / "science" / "models.yml"
    models_dst = (
        (Path.home() / os.environ.get("PI_CONFIG_DIR", ".omp") / "profiles" / args.profile)
        / "agent"
        / "models.yml"
    )
    installed = models_dst.is_file() and models_dst.read_bytes() == models_src.read_bytes()
    report.check(
        installed,
        "credenciais emprestadas do perfil padrão",
        ""
        if installed
        else f"{models_dst} difere de .omp/science/models.yml: rode scripts/omp-science",
    )
    logged = {}
    for provider in MODEL_PROVIDERS_NEEDED:
        result = subprocess.run(
            ["omp", "--profile", args.profile, "token", provider],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=os.environ,
        )
        logged[provider] = result.returncode == 0
        if not logged[provider]:
            report.warn(
                f"credencial {provider}", f"ausente no OMP normal: rode `omp login {provider}`"
            )
        else:
            report.check(True, f"credencial {provider}")

    # 3. Composed session.
    state, commands, stderr = rpc_session(args.profile, context, args.timeout)
    if not state:
        detail = stderr.strip().splitlines()[-1] if stderr.strip() else "sem resposta"
        if all(logged.values()):
            report.check(False, "sessão RPC", detail)
        else:
            report.warn("sessão RPC", f"não iniciou sem login: {detail}")
    else:
        prompt = "\n".join(state.get("systemPrompt") or [])
        model = state.get("model") or {}
        report.check(
            bool(model), "modelo da sessão principal", f"{model.get('provider')}/{model.get('id')}"
        )
        report.check("Invariantes científicos deste repositório" in prompt, "RULES.md fixado")
        report.check(
            "Ambiente de escrita científica — IVF/SPEA2" in prompt, "contexto científico anexado"
        )
        report.check(str(root / "CLAUDE.md") not in prompt, "CLAUDE.md fora do contexto")
        for name in sorted(expected["skills"]):
            report.check(
                re.search(rf"^- {re.escape(name)}:", prompt, re.M) is not None, f"skill {name}"
            )
        task_tool = next((t for t in state.get("dumpTools") or [] if t.get("name") == "task"), {})
        task_text = json.dumps(task_tool, ensure_ascii=False)
        for name in sorted(expected["agents"]):
            report.check(name in task_text, f"agente {name}")
        command_names = {c.get("name") for c in commands}
        for name in sorted(expected["commands"]):
            report.check(name in command_names, f"comando /{name}")
        skills_block = "\n".join(re.findall(r"^- ([\w:-]+):", prompt, re.M))
        leaked = sorted(
            n
            for n in foreign_names(root)
            if n not in expected["skills"] | expected["agents"] | expected["commands"]
            and (re.search(rf"^{re.escape(n)}$", skills_block, re.M) or n in command_names)
        )
        report.check(not leaked, "nada de outros harnesses", str(leaked))

    if args.json:
        keys = ("status", "check", "detail")
        print(json.dumps([dict(zip(keys, r, strict=True)) for r in report.rows], indent=2))
    else:
        for status, name, detail in report.rows:
            print(f"{status:4} {name}" + (f" — {detail[:110]}" if detail else ""))
    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main())
