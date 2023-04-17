# ansible-aisnippet

## Features

## Quickstart

### Install python package

Install the latest version `ansible-aisnippet` with `pip` or `pipx`

```bash
pip install ansible-aisnippet
```

### Usage

You must have an openai.api_key. You can create it from [openai](https://platform.openai.com/account/api-keys) website.

```bash
export  OPENAI_KEY=<your token>

ansible-aisnippet --help

 Usage: ansible-aisnippet [OPTIONS] COMMAND [ARGS]...

╭─ Options ─────────────────────────────────────────────────────╮
│ --version             -v        Show the application's        │
│                                 version and exit.             │
│ --install-completion            Install completion for the    │
│                                 current shell.                │
│ --show-completion               Show completion for the       │
│                                 current shell, to copy it or  │
│                                 customize the installation.   │
│ --help                          Show this message and exit.   │
╰───────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────╮
│ generate  Ask ChatGPT to write an ansible task using a        │
│           template                                            │
╰───────────────────────────────────────────────────────────────╯
```

### Generate task(s)

ansible-aisnippet can generate an or several ansible task from a description or
a filetasks.

```bash
ansible-aisnippet generate --help

 Usage: ansible-aisnippet generate [OPTIONS] [TEXT]

 Ask ChatGPT to write an ansible task using a template

╭─ Arguments ──────────────────────────────────────────────────────────────────────╮
│   text      [TEXT]  A description of task to get [default: Install package htop] │
╰──────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────╮
│ --verbose     -v            verbose mode                                         │
│ --filetasks   -f      PATH  [default: None]                                      │
│ --outputfile  -o      PATH  [default: None]                                      │
│ --playbook    -p            Create a playbook                                    │
│ --help                      Show this message and exit.                          │
╰──────────────────────────────────────────────────────────────────────────────────╯
```

#### Generate a task

```bash
export  OPENAI_KEY=<your token>

ansible-aisnippet generate "execute command to start /opt/application/start.sh create /var/run/test.lock"
Building prefix dict from the default dictionary ...
Loading model from cache /tmp/jieba.cache
Loading model cost 0.686 seconds.
Prefix dict has been built successfully.
name: Execute command to start /opt/application/start.sh create /var/run/test.lock

ansible.builtin.command:
  chdir: /opt/application
  cmd: ./start.sh && touch /var/run/test.lock
  creates: /var/run/test.lock
  removes: ''
```

#### Generate severals tasks

ansible-aisnippet can generate severals tasks from a file. The file is a yaml file which contains a list of tasks and blocks

Ex:

```yaml
- task: Install package htop, nginx and net-tools with generic module
- task: Copy file from local file /tmp/toto to remote /tmp/titi set mode 0666 owner bob group www
  register: test
- name: A block
  when: test.rc == 0
  block:
    - task: wait for port 6300 on localhost timeout 25
  rescue:
    - task: Execute command /opt/application/start.sh creates /var/run/test.lock
- task: Download file from https://tmp.io/test/ set mode 0640 and force true
```

This file produces this result :

```bash
export  OPENAI_KEY=<your token>

ansible-aisnippet generate -f test.yml -p
Building prefix dict from the default dictionary ...
Loading model from cache /tmp/jieba.cache
Loading model cost 0.671 seconds.
Prefix dict has been built successfully.
Result:

- name: Playbook generated with chatgpt
  hosts: all
  gather_facts: true
  tasks:
  - name: Install package htop, nginx and net-tools
    ansible.builtin.yum:
      name:
      - htop
      - nginx
      - net-tools
      state: present
  - name: Copy file from local file /tmp/toto to remote /tmp/titi
    ansible.builtin.copy:
      src: /tmp/toto
      dest: /tmp/titi
      mode: '0666'
      owner: bob
      group: www
    register: test
  - name: A block
    when: test.rc == 0
    block:
    - name: Wait for port 6300 on localhost timeout 25
      ansible.builtin.wait_for:
        host: 127.0.0.1
        port: '6300'
        timeout: '25'
    rescue:
    - name: Execute command /opt/application/start.sh creates /var/run/test.lock
      ansible.builtin.command:
        chdir: /tmp/test
        cmd: /opt/application/start.sh
        creates: /var/run/test.lock
  - name: Download file from https://tmp.io/test/
    ansible.builtin.get_url:
      backup: false
      decompress: true
      dest: /tmp/test
      force: true
      group: root
      mode: '0640'
      owner: root
      timeout: '10'
      tmp_dest: /tmp/test
      url: https://tmp.io/test/
      validate_certs: true
```
