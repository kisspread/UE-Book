# Switchboard

> Launcher/Installer for the Switchboard application.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（OSC 资产、Python 应用脚本） |
| 模块 | `SwitchboardCommon` (Runtime), `SwitchboardEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-09 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Switchboard) | |

## 用途

Switchboard 是 Epic Games 为 **虚拟制片 (Virtual Production)** 工作流打造的一站式设备编排与录制管理工具。它本质上是一个独立的 Python/PySide6 桌面应用，通过 UE 编辑器插件作为"启动器/安装器"来集成。

Switchboard 解决的核心问题是：在 LED Volume（nDisplay）拍摄现场，需要同时协调多种异构设备——多个 Unreal Engine 实例、nDisplay 集群、音频录制器（Sound Devices）、摄影机记录器（AJA KiPro）、Live Link Hub 等——并统一管理它们的连接、同步、构建、启动和 Take 录制。手动逐个操作这些设备既低效又容易出错，Switchboard 提供了一个统一的 GUI 面板来集中控制。

它通过 **OSC (Open Sound Control)** 协议与各设备通信，通过 **QUIC 协议**（基于 aioquic）与 Switchboard Listener 进行安全连接，实现设备的远程管理。

## 使用场景

- 你在搭建一个 **LED Volume / nDisplay ICVFX** 拍摄环境，需要同时管理多个 UE 实例和 nDisplay 节点 → 用 Switchboard
- 你需要在一个界面中**同步录制 Take**（Slate/Take 编号、多设备同步开始/停止录制）→ 用 Switchboard
- 你需要远程 **构建、同步 Perforce changelist、启动/关闭** 多台机器上的 UE → 用 Switchboard
- 你需要管理 **Sound Devices 音频录制器** 或 **AJA KiPro 摄影机记录器** 的录制状态 → 用 Switchboard
- 你需要在拍摄现场使用 **Live Link Hub** 进行面部/身体动捕数据分发 → 用 Switchboard

## 架构概览

Switchboard 的架构分为两部分：

### 1. UE 编辑器插件（C++ 部分）

编辑器插件 (`SwitchboardEditor`) 作为 **启动器和安装向导**，负责：

- 在 UE 编辑器的工具栏/菜单中添加 Switchboard 入口
- 管理 Python 虚拟环境路径配置（`USwitchboardEditorSettings`）
- 管理项目级 OSC 监听器配置（`USwitchboardProjectSettings`）
- 编译 Switchboard Listener（通过 UBT）
- 安装向导（Setup Wizard）：安装依赖、创建桌面快捷方式、配置 Listener 自启动
- 从编辑器内快速创建新配置（传入当前地图、nDisplay Config 等）
- 管理 Listener 自启动（Windows 注册表，仅 Win64）

### 2. Switchboard Python 应用

独立的 PySide6 桌面应用，位于 `Source/Switchboard/switchboard/`，负责实际的设备管理：

| 模块 | 说明 |
|---|---|
| `switchboard_dialog.py` | 主窗口 UI 和交互逻辑 |
| `switchboard_application.py` | 核心应用逻辑，OSC 服务器，设备命令行管理 |
| `config.py` | 配置系统（JSON 配置文件、用户设置） |
| `recording.py` | Take 录制管理（RecordingManager） |
| `listener_client.py` | QUIC 安全连接客户端，与 Switchboard Listener 通信 |
| `message_protocol.py` | 设备间消息协议（认证、同步状态请求等） |
| `device_manager.py` | 设备插件发现和管理 |
| `devices/device_base.py` | 设备基类（Device、DeviceStatus 状态机） |

### 3. 设备插件系统

Switchboard 通过 **设备插件** 支持多种硬件/软件：

| 插件 | 设备类型 | 说明 |
|---|---|---|
| `plugin_unreal.py` | Unreal Engine 实例 | 核心设备，管理 UE 的构建、同步、启动、录制 |
| `plugin_ndisplay.py` | nDisplay 集群 | ICVFX LED Volume 的多屏渲染集群管理 |
| `plugin_ndisplayTest.py` | nDisplay 测试 | nDisplay 自动化测试设备 |
| `plugin_sounddevices.py` | Sound Devices | 音频录制器（通过 HTTP API 控制） |
| `plugin_kipro.py` | AJA KiPro | 摄影机记录器（通过 REST API 控制） |
| `plugin_livelinkhub.py` | Live Link Hub | 面部/身体动捕数据分发中心 |

设备通过插件系统自动发现——`DeviceManager` 扫描 `switchboard/devices/` 下的 Python 包，找到 `Device` 子类和对应的 Widget 类。

### 4. Switchboard Listener

一个独立编译的 C++ 程序（通过 UBT 编译），运行在每台受控机器上，负责：
- 接收 Switchboard 的 QUIC 连接
- 执行本地操作（启动 UE、构建、同步等）
- 回报设备状态

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSwitchboardProjectSettings` | 获取 Switchboard 项目设置单例 | `USwitchboardProjectSettings` |
| `GetSwitchboardEditorSettings` | 获取 Switchboard 编辑器设置单例 | `USwitchboardEditorSettings` |

Switchboard 的主要功能通过其独立 Python GUI 操作，蓝图中的暴露非常有限。项目设置主要用于配置 OSC 监听器。

### 项目设置（Project Settings → Plugins → Switchboard）

- **Default Switchboard OSC Listener**：指定 Switchboard 使用的 OSC 资产路径（默认 `/Switchboard/OSCSwitchboard`）。Switchboard 默认使用端口 8000。

### 编辑器设置（Editor Preferences → Plugins → Switchboard）

- **Virtual Environment Path**：Python 虚拟环境路径，第三方依赖安装于此
- **Listener Commandline Arguments**：传递给 Switchboard Listener 的命令行参数

## C++ 用法

### 头文件引入

```cpp
#include "SwitchboardEditorSettings.h"
#include "SwitchboardProjectSettings.h"
```

### 基本用法：访问设置

```cpp
// 获取编辑器设置（虚拟环境路径、Listener 参数）
USwitchboardEditorSettings* EditorSettings = GetDefault<USwitchboardEditorSettings>();
FString VenvPath = EditorSettings->VirtualEnvironmentPath.Path;

// 获取项目设置（OSC 监听器）
USwitchboardProjectSettings* ProjectSettings = GetDefault<USwitchboardProjectSettings>();
FSoftObjectPath OSCListener = ProjectSettings->SwitchboardOSCListener;
```

### 编辑器模块 API

```cpp
#include "SwitchboardEditorModule.h"

FSwitchboardEditorModule& SBModule = FSwitchboardEditorModule::Get();

// 启动 Switchboard 应用
SBModule.LaunchSwitchboard(TEXT("--config MyConfig"));

// 编译 Switchboard Listener
SBModule.CompileSwitchboardListener();

// 启动 Switchboard Listener
SBModule.LaunchListener();

// 检查安装状态
auto InstallState = SBModule.GetSwitchboardInstallState();
// ESwitchboardInstallState: Nominal, NeedInstallOrRepair, ShortcutsMissing, VerifyInProgress

// 获取验证结果（检查 venv 是否正确安装）
TSharedFuture<FSwitchboardVerifyResult> Result = SBModule.GetVerifyResult();
```

### 创建新配置（从编辑器）

```cpp
#include "SwitchboardTypes.h"

FSwitchboardNewConfigUserOptions Options;
Options.ConfigName = TEXT("MyICVFXSetup");
Options.bUseLocalhost = true;
Options.bAutoConnect = true;
Options.NumEditorDevices = 2;
Options.DCRA.DCRA = MyDisplayClusterRootActor;  // nDisplay 根 Actor 引用

FSwitchboardEditorModule::Get().CreateNewConfig(Options);
```

### Listener 自启动管理（仅 Win64）

```cpp
#if SWITCHBOARD_LISTENER_AUTOLAUNCH
// 检查是否已配置自启动
bool bEnabled = SBModule.IsListenerAutolaunchEnabled();

// 设置自启动
SBModule.SetListenerAutolaunchEnabled(true);

// 移除自启动
SBModule.SetListenerAutolaunchEnabled(false);
#endif
```

## 模块依赖

`SwitchboardEditor` 模块的依赖（`PrivateDependencyModuleNames`）：

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `UnrealEd` | 编辑器框架 |
| `Slate` / `SlateCore` | UI 框架 |
| `PropertyEditor` | 属性自定义面板 |
| `Settings` | 设置注册系统 |
| `DesktopPlatform` | 平台抽象（进程启动、UBT 调用） |
| `AssetRegistry` | 资产注册表 |
| `Json` / `JsonUtilities` | JSON 序列化（配置传递） |
| `Projects` | 插件管理 |
| `ToolMenus` | 工具栏/菜单扩展 |
| `ToolWidgets` | 编辑器工具 Widget |
| `SwitchboardCommon` | 跨平台公共功能（Listener 自启动） |
| `InputCore` | 输入系统 |
| `MessageLog` | 消息日志 |
| `Blutility` | 蓝图实用工具 |

`SwitchboardCommon` 模块仅依赖 `Core`。

Python 端的主要依赖：`PySide6`（Qt GUI）、`pythonosc`（OSC 通信）、`aioquic`（QUIC 协议）、`cryptography`（证书/认证）。

## 维护状态

### 近期更新

1. `ad97d2e2cd54` | 2025-11-18 | `Switchboard: Syncstatus fixes for "Engine Sync Method" == "Use Existing", sync filters.`
   - 修复了使用 "Use Existing" 引擎同步方法时的状态同步问题，改进了同步过滤器
2. `aa9f6cf9a62a` | 2025-09-30 | `Switchboard: Disable base class validation in nDisplay device creation dialog.`
   - 禁用了 nDisplay 设备创建对话框中的基类验证，简化设备添加流程
3. `a3b61c1fe664` | 2025-09-26 | `Switchboard: Add support for suppressing LLH crash recovery, make Unreal OSC endpoint args unconditional.`
   - 新增 Live Link Hub 崩溃恢复抑制支持，改进 Unreal OSC 端点参数处理

### 维护评价

- **活跃维护**：最近 6 个月内有功能性更新
- 标记为 `IsBetaVersion=true`（实验性），说明 Epic 仍在迭代中
- `EnabledByDefault=false`，需要手动启用
- 仅支持 Win64 和 Linux 平台
- 这是 Epic Virtual Production 团队的核心工具之一，用于其自身的 ICVFX 工作流，维护质量有保障
- Listener 自启动功能仅限 Win64（依赖 Windows 注册表）
- **推荐使用**：如果你在搭建 LED Volume / nDisplay 拍摄环境，这是官方推荐的设备编排工具

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Switchboard)
- 官方文档：无（.uplugin 的 DocsURL 为空）
- 依赖插件：[OSC](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/OSC)、[Takes](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes)、[VirtualProductionUtilities](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualProductionUtilities)
