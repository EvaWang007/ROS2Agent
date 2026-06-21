# ROSA + ROS2 导航仿真中文运行手册

本文档面向当前仓库，目标是在一台新机器上从零跑通：

- Gazebo 房屋仿真
- Nav2 定位与路径规划
- 巡航节点 `robot_patrol`
- 自然语言 Agent `nav_agent_ros2`


## 1. 前置条件

推荐环境：

- Ubuntu 22.04
- ROS2 Humble
- Conda（用于 Agent Python 环境）

建议安装的 ROS 组件：

```bash
sudo apt update
sudo apt install -y \
  ros-humble-desktop \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-nav2-bringup \
  ros-humble-slam-toolbox \
  ros-humble-robot-localization \
  ros-humble-nav2-simple-commander \
  ros-humble-cv-bridge \
  ros-humble-xacro
```


## 2. 克隆与 Python 环境

```bash
git clone <your-repo-url>
cd rosa-main
conda env create -f environment.yml
conda activate rosa
pip install -e .[memory]
```


## 3. 配置 LLM

当前 `nav_agent_ros2` 默认走 DeepSeek 兼容接口：

```bash
export DEEPSEEK_API_KEY=你的密钥
export DEEPSEEK_BASE_URL=https://api.deepseek.com
export DEEPSEEK_MODEL=deepseek-chat
```

建议同时设置：

```bash
export ROSA_PYTHON=$(which python)
```

这样 `agent.launch.py` 会使用当前 conda 解释器，而不是作者本地写死的路径。


## 4. 构建 ROS 工作区

```bash
cd nav_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

也可以使用：

```bash
bash build_nav.sh
```

但这个脚本里有硬编码的 `ROOT` 路径，换服务器时要先改。


## 5. 启动顺序

建议用 4~5 个终端分别启动。


### 终端 1：Gazebo 仿真

```bash
cd /path/to/rosa-main/nav_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch robot_simulation house_sim.launch.py use_sim_time:=True
```


### 终端 2：Nav2

```bash
cd /path/to/rosa-main/nav_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch robot_simulation autonomous_navigation.launch.py use_sim_time:=True map_file_path:=./src/robot_simulation/maps/house_map.yaml
```


### 终端 3：自动巡航

```bash
cd /path/to/rosa-main/nav_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run robot_patrol robot_patrol
```


### 终端 4：自然语言 Agent

```bash
cd /path/to/rosa-main
conda activate rosa
export ROSA_PYTHON=$(which python)
export DEEPSEEK_API_KEY=你的密钥
export DEEPSEEK_BASE_URL=https://api.deepseek.com
export DEEPSEEK_MODEL=deepseek-chat
source /opt/ros/humble/setup.bash
source nav_ws/install/setup.bash
ros2 launch nav_agent_ros2 agent.launch.py streaming:=true
```


### 终端 5：可选视觉检测节点

```bash
cd /path/to/rosa-main
conda activate rosa
source /opt/ros/humble/setup.bash
source nav_ws/install/setup.bash
python nav_ws/src/nav_agent_ros2/nav_agent_ros2/yolo_detector.py
```


## 6. 推荐验证命令

启动成功后，可以在 Agent 命令行输入：

- `List ROS2 nodes/topics/services in current graph.`
- `Get one odom snapshot.`
- `Get one scan snapshot.`
- `Publish a tiny cmd_vel command for 0.5 seconds.`


## 7. 一键脚本

仓库内已有：

```bash
bash nav_ws/start_sim.sh
```

它会自动启动：

- `house_sim.launch.py`
- `autonomous_navigation.launch.py`
- `robot_patrol`

同样注意它包含硬编码路径，迁移服务器时要先改脚本里的 `ROOT`。


## 8. 常见问题

### Agent 启动失败，提示 Python 路径错误

```bash
export ROSA_PYTHON=$(which python)
```


### Agent 启动成功，但模型调用失败

检查：

```bash
echo $DEEPSEEK_API_KEY
echo $DEEPSEEK_BASE_URL
echo $DEEPSEEK_MODEL
```


### 导航不工作

优先检查：

- 仿真是否已先启动
- `/tf`、`/odom`、`/scan` 是否存在
- Nav2 是否已 Active
- 初始位姿是否正确


### 地图文件加载失败

请确保在 `nav_ws` 根目录执行 Nav2 启动命令，或改用绝对路径。
