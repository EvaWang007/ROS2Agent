<!-- Header block for project --> <hr>
<div align="center">
<!--   <img width="292" alt="ROSA_logo_dark_bg@2x" src="https://github.com/user-attachments/assets/7b4a8e64-9a08-4180-806a-5076d3672c05"> -->
<!--   <img width="213" alt="ROSA_sticker_color@2x" src="https://github.com/user-attachments/assets/5fa3a03e-5ef8-4942-84ac-95acf2f1777d"> -->
<!--   <img width="426" alt="ROSA_sticker_color@2x" src="https://github.com/user-attachments/assets/98b0a0ed-6b14-420c-83af-9067ab2d2d22"> -->
<!-- <img src="https://github.com/user-attachments/assets/d7175d5e-63d2-448c-b9d3-59ca0016ef7a"> -->
<img width="2057" alt="image" src="https://github.com/user-attachments/assets/ddbd3281-79f0-4d29-b0cd-30a5188ad061">

  
</div>
<div align="center">
  ROS Agent（ROSA）旨在通过自然语言与基于 ROS 的<br>机器人系统交互。🗣️🤖
</div>
<br>
<div align="center">

[![arXiv](https://img.shields.io/badge/arXiv-2410.06472-b31b1b.svg)](https://arxiv.org/abs/2410.06472)
![ROS 1](https://img.shields.io/badge/ROS_1-Noetic-blue)
![ROS 2](https://img.shields.io/badge/ROS_2-Humble|Iron|Jazzy-blue)
![License](https://img.shields.io/pypi/l/jpl-rosa)
[![SLIM](https://img.shields.io/badge/Best%20Practices%20from-SLIM-blue)](https://nasa-ammos.github.io/slim/)

![Main Branch](https://img.shields.io/github/actions/workflow/status/nasa-jpl/rosa/ci.yml?branch=main&label=main)
![Dev Branch](https://img.shields.io/github/actions/workflow/status/nasa-jpl/rosa/ci.yml?branch=dev&label=dev)
![Publish Status](https://img.shields.io/github/actions/workflow/status/nasa-jpl/rosa/publish.yml?label=publish)
![Version](https://img.shields.io/pypi/v/jpl-rosa)
![Downloads](https://img.shields.io/pypi/dw/jpl-rosa)

</div>
<!-- Header block for project -->

> [!IMPORTANT]
> 📚 **第一次接触 ROSA？** 建议先阅读我们的 [Wiki](https://github.com/nasa-jpl/rosa/wiki)，里面有文档、指南和 FAQ。


ROSA 是一个面向 ROS1 / ROS2 系统的 AI Agent。它基于 [LangChain](https://python.langchain.com/v0.2/docs/introduction/) 构建，可以把自然语言指令转化为对机器人系统的查询、分析与操作，让机器人开发、调试和演示更加高效。

#### ROSA 演示：JPL Mars Yard 中的 NeBula-Spot（点击跳转 YouTube）
[![Spot YouTube Thumbnail](https://github.com/user-attachments/assets/19a99b5c-6103-4be4-8875-1810cf4558c5)](https://www.youtube.com/watch?v=mZTrSg7tEsA)


## 🚀 快速开始

### 环境要求
- Python 3.9+
- ROS Noetic 或更高版本

### 安装
```bash
pip3 install jpl-rosa
```

### 使用示例

```python
from rosa import ROSA

llm = get_your_llm_here()
agent = ROSA(ros_version=1, llm=llm)
agent.invoke("Show me a list of topics that have publishers but no subscribers")
```

关于 LLM 的详细配置方式，请参考我们的 [Model Configuration Wiki page](https://github.com/nasa-jpl/rosa/wiki/Model-Configuration)。


## 在另一台服务器上复现当前仓库

如果你要完整复现这个仓库当前快照，建议以仓库中的 `environment.yml` 作为 Python 环境基线：

```bash
conda env create -f environment.yml
conda activate rosa
pip install -e .[memory]
```

然后重新从源码构建 ROS2 工作区，而不是依赖任何已生成的构建产物：

```bash
source /opt/ros/<your_distro>/setup.bash
cd nav_ws
colcon build --symlink-install
source install/setup.bash
```

如果你计划运行 `nav_ws/src/nav_agent_ros2` 中的 ROS2 导航 Agent 扩展，请确保目标机器还具备以下条件：

- 已安装并正确 `source` 的 ROS2
- ROS 环境中可用的 `cv_bridge`
- 仓库根目录下已提交的 `yolov8n.pt` 权重文件

本仓库刻意不再纳入 `install/`、`log/`、`logs/` 等运行生成目录，以便跨机器时能从源码干净重建环境。


## 中文从 0 运行手册

这一节面向你当前这个仓库里的 ROS2 仿真导航工程，目标是从一台新机器开始，最终跑通：

- Gazebo 房屋仿真
- Nav2 定位与导航
- 巡航节点 `robot_patrol`
- 自然语言导航 Agent `nav_agent_ros2`


### 1. 系统前置依赖

建议使用 Ubuntu + ROS2 Humble。至少需要：

- ROS2 Humble
- Gazebo / `gazebo_ros`
- `nav2_bringup`
- `slam_toolbox`
- `robot_localization`
- `nav2_simple_commander`
- `cv_bridge`
- `xacro`

如果使用 apt 安装，通常会接近下面这组：

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


### 2. 克隆仓库并准备 Python 环境

```bash
git clone <your-repo-url>
cd rosa-main
conda env create -f environment.yml
conda activate rosa
pip install -e .[memory]
```

如果后续你要让 ROS2 Agent 使用当前 conda Python，建议记住下面这个环境变量：

```bash
export ROSA_PYTHON=$(which python)
```

`nav_ws/src/nav_agent_ros2/launch/agent.launch.py` 会优先使用 `ROSA_PYTHON`；不设置时，它默认写死到作者本机路径，因此在新服务器上最好显式设置。


### 3. 配置 LLM 密钥

当前 ROS2 导航 Agent 使用的是 DeepSeek 兼容接口，至少需要配置：

```bash
export DEEPSEEK_API_KEY=你的密钥
export DEEPSEEK_BASE_URL=https://api.deepseek.com
export DEEPSEEK_MODEL=deepseek-chat
```

你也可以把这些变量写入仓库根目录的 `.env` 文件中，程序会自动读取。


### 4. 构建 `nav_ws`

推荐先用系统 Python 构建 ROS 工作区：

```bash
cd nav_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

仓库中也提供了辅助脚本：

```bash
bash nav_ws/build_nav.sh
```

但要注意：`nav_ws/build_nav.sh` 里有硬编码仓库路径，如果你把仓库放到了别的目录，需要先修改脚本中的 `ROOT` 变量。


### 5. 启动仿真系统

建议至少开 4 个终端，分别运行仿真、导航、巡航和 Agent。

#### 终端 1：启动 Gazebo 房屋仿真

```bash
cd /path/to/rosa-main/nav_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch robot_simulation house_sim.launch.py use_sim_time:=True
```

这一步会完成：

- Gazebo 世界加载
- 机器人模型加载
- `robot_state_publisher`
- `ekf_node`
- RViz 启动
- `map -> odom` 的静态 TF 发布


#### 终端 2：启动 Nav2 定位与导航

```bash
cd /path/to/rosa-main/nav_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch robot_simulation autonomous_navigation.launch.py use_sim_time:=True map_file_path:=./src/robot_simulation/maps/house_map.yaml
```

这里会拉起：

- `localization_launch.py`
- `navigation_launch.py`
- AMCL
- `bt_navigator`
- `planner_server`
- `controller_server`
- 全局/局部 costmap

注意：这里的 `map_file_path` 默认写的是相对路径，所以最稳妥的方式就是在 `nav_ws` 根目录下执行这条命令。


#### 终端 3：启动自动巡航节点

```bash
cd /path/to/rosa-main/nav_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run robot_patrol robot_patrol
```

这个节点内部基于 `nav2_simple_commander.BasicNavigator`，会：

- 设置初始位姿
- 等待 Nav2 进入 Active
- 按预设 waypoint 进行巡航

如果你暂时只想验证 Nav2 和 Agent，这一步可以先不启动。


### 6. 启动 ROS2 自然语言 Agent

#### 终端 4：启动 `nav_agent_ros2`

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

启动后你会得到一个交互式命令行，支持：

- `help`
- `examples`
- `clear`
- `exit`

你可以直接输入类似：

- `List ROS2 nodes/topics/services in current graph.`
- `Get one odom snapshot.`
- `Get one scan snapshot.`
- `Publish a tiny cmd_vel command for 0.5 seconds.`
- `Run ros2 doctor and summarize issues.`


### 7. 可选：启动 YOLO 检测节点

如果你还想启用视觉检测，可再开一个终端：

```bash
cd /path/to/rosa-main
conda activate rosa
source /opt/ros/humble/setup.bash
source nav_ws/install/setup.bash
python nav_ws/src/nav_agent_ros2/nav_agent_ros2/yolo_detector.py
```

该节点会：

- 订阅 `/camera_sensor/image_raw`
- 使用 `yolov8n.pt` 进行检测
- 将结果发布到 `/perception/detections_text`


### 8. 一键脚本说明

仓库中还有一个一键启动脚本：

```bash
bash nav_ws/start_sim.sh
```

它会顺序执行：

- 加载 ROS 环境
- 启动 `house_sim.launch.py`
- 启动 `autonomous_navigation.launch.py`
- 启动 `robot_patrol`

但同样要注意：

- 脚本中的 `ROOT` 是硬编码路径
- 脚本默认假设你使用 ROS Humble
- 更适合作者本地环境，迁移到新服务器时建议优先使用上面的分终端手册


### 9. 常见问题排查

#### `nav_agent_ros2` 启动时报 Python 路径不对

优先检查：

```bash
echo $ROSA_PYTHON
```

建议设置为当前 conda 环境解释器：

```bash
export ROSA_PYTHON=$(which python)
```


#### Agent 能启动，但调用 LLM 时报密钥错误

检查：

```bash
echo $DEEPSEEK_API_KEY
echo $DEEPSEEK_BASE_URL
echo $DEEPSEEK_MODEL
```


#### Nav2 启动了，但机器人不动

优先检查：

- `house_sim.launch.py` 是否已经先启动
- `autonomous_navigation.launch.py` 是否成功进入 Active
- `/tf`、`/odom`、`/scan` 是否正常发布
- 初始位姿是否正确


#### `map_file_path` 找不到地图

请确认你是在 `nav_ws` 根目录执行：

```bash
ros2 launch robot_simulation autonomous_navigation.launch.py use_sim_time:=True map_file_path:=./src/robot_simulation/maps/house_map.yaml
```

或者把它改成绝对路径。


## 如何为你的机器人定制 ROSA 🔧

ROSA 的设计目标之一就是方便扩展到不同机器人和不同环境。你可以通过继承 `ROSA` 类，或者直接基于它创建自定义实例，来快速构建属于你自己的机器人 Agent。

关于如何创建自定义 Agent、增加工具、定制 prompt，请参考 [Custom Agents Wiki page](https://github.com/nasa-jpl/rosa/wiki/Custom-Agents)。


## TurtleSim 演示 🐢

仓库中包含一个使用 ROSA 控制 TurtleSim 的示例。运行该示例需要你本机安装 Docker。🐳

下面这个视频展示了 ROSA 如何先推理“如何画一个五角星”，然后再执行相应命令。

https://github.com/user-attachments/assets/77b97014-6d2e-4123-8d0b-ea0916d93a4e

详细运行说明请参考 Wiki 中的 [TurtleSim Demo Guide](https://github.com/nasa-jpl/rosa/wiki/Guide:-TurtleSim-Demo)。


## IsaacSim 扩展（即将推出）

ROSA 正在扩展到 Nvidia IsaacSim。你现在已经可以通过 ROS / ROS2 Bridge 把 ROSA 接到 IsaacSim 中运行；后续我们还会增加更直接的 IsaacSim 扩展能力，使你不仅能控制机器人，也能直接控制 IsaacSim 本身。

#### ROSA 演示：Nvidia IsaacSim Extension（点击跳转 YouTube）
[![Carter YouTube Thumbnail Play](https://github.com/user-attachments/assets/a6948d5e-2726-4dd8-8dee-19dfb5188f1d)](https://www.youtube.com/watch?v=mm5525G_EfQ)


## 📘 进一步了解

- [📕 论文](https://arxiv.org/abs/2410.06472)
- [🗺️ 功能路线图](https://github.com/nasa-jpl/rosa/wiki/Feature-Roadmap)
- [🏷️ 版本发布](https://github.com/nasa-jpl/rosa/releases)
- [❓ 常见问题 FAQ](https://github.com/nasa-jpl/rosa/wiki/FAQ)


## 更新日志

变更历史请查看 [CHANGELOG.md](CHANGELOG.md)。


## 参与贡献

如果你对本项目感兴趣并希望参与，请先阅读：[CONTRIBUTING.md](CONTRIBUTING.md)

关于与项目团队协作的行为规范，请参考：[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

关于治理方式、角色分工和决策机制，请参考：[GOVERNANCE.md](GOVERNANCE.md)


## 许可证

请查看：[LICENSE](LICENSE)


## 支持与联系

主要联系人如下：

- [@RobRoyce](https://github.com/RobRoyce) ([email](mailto:01-laptop-voiced@icloud.com))

---

<div align="center">
  ROSA: Robot Operating System Agent 🤖<br>
  Copyright (c) 2024. Jet Propulsion Laboratory. All rights reserved.
</div>
