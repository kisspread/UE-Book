# Remote Control Web Interface

> Provides a web interface to control unreal engine via presets, requires nodejs to be installed

| 属性 | 值 |
|---|---|
| 分类 | VirtualProduction |
| 默认启用 | 是 (Editor 模式下自动启动) |
| 包含内容 | 是 (WebApp 前端资源) |
| 模块 | RemoteControlWebInterface (Runtime) |
| 创建时间 | 2020-12-11 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControlWebInterface) | |

## 用途

Remote Control Web Interface 是 UE5 虚拟制片工具链的一部分，它在 RemoteControl / WebRemoteControl 插件之上提供了一个**基于浏览器的 Web 前端**。

核心工作原理：
1. 编辑器启动时，自动在后台启动一个 Node.js Web 服务进程（中继服务器）
2. 该 Web 服务连接到 UE 的 Remote Control WebSocket 和 HTTP 服务器
3. 用户通过浏览器访问 Web 界面，可以查看和控制通过 Remote Control Preset 暴露的属性、函数
4. Web 前端还支持为属性自定义 Widget 类型（Slider、Dial、Color Picker、Toggle 等）

简而言之：它让你能用浏览器远程控制 UE 编辑器中的任意暴露属性，非常适合虚拟制片场景下的灯光、摄像机、材质参数实时调节。

## 使用场景

- 你在做**虚拟制片**，需要从 iPad 或另一台电脑的浏览器实时调整场景灯光、摄像机参数
- 你需要给导演/灯光师一个简单的 Web 界面来控制 UE 中的属性，而不需要给他们整个编辑器
- 你需要将 UE 的属性暴露给外部设备（平板、手机）进行远程操控
- 你需要为不同的属性选择不同的 Web Widget（滑块、旋钮、颜色选择器等）

## 蓝图用法

本插件提供了一个 `URCWebInterfaceBlueprintLibrary` 蓝图函数库，主要用于在 Web 界面中实现属性重绑定（Rebind）功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindMatchingActorsToRebind` | 查找可重绑定的兼容 Actor 列表（返回 Map: Label → Actor） | `URCWebInterfaceBlueprintLibrary` |
| `GetOwnerActorLabel` | 获取 RC Preset 属性的拥有者 Actor 名称，多个所有者时返回空 | `URCWebInterfaceBlueprintLibrary` |
| `RebindProperties` | 将 RC Preset 属性重绑定到新的 Actor | `URCWebInterfaceBlueprintLibrary` |
| `FindAllActorsOfClass` | 查找指定类的所有 Actor | `URCWebInterfaceBlueprintLibrary` |
| `SpawnActor` | 生成指定类的 Actor | `URCWebInterfaceBlueprintLibrary` |
| `GetValuesOfActorsByClass` | 获取指定类所有 Actor 的属性值（JSON 格式） | `URCWebInterfaceBlueprintLibrary` |

### 使用示例（蓝图描述）

**查找可重绑定的 Actor：**
1. 创建一个 Blueprint，添加按钮事件
2. 调用 `FindMatchingActorsToRebind`，传入 PresetId 和 PropertyIds 数组
3. 返回的 Map 包含所有匹配的 Actor，可用于 UI 展示供用户选择

**重绑定属性到新 Actor：**
1. 用户在 Web 界面选择要重绑定的属性
2. 调用 `GetOwnerActorLabel` 获取当前所有者
3. 调用 `RebindProperties` 将属性绑定到用户选择的新 Actor

## C++ 用法

### 头文件引入

```cpp
#include "RCWebInterface.h"
#include "RCWebInterfaceProcess.h"
#include "RCWebInterfaceLibrary.h"
```

### 基本用法 — 控制 WebApp 进程

WebApp 进程在模块启动时自动管理，通常不需要手动操作。但可以通过控制台命令控制：

```cpp
// 通过控制台命令控制 WebApp（模块内部通过 FSelfRegisteringExec 实现）
// 控制台命令格式: RCWebInterface Start / Stop / Restart

// 也可以直接访问模块
FRemoteControlWebInterfaceModule& Module = FRemoteControlWebInterfaceModule::Get();
```

### 基本用法 — 蓝图库函数

```cpp
// 查找可重绑定的 Actor
TMap<FString, AActor*> Matches = URCWebInterfaceBlueprintLibrary::FindMatchingActorsToRebind(
    PresetId, PropertyIds);

// 重绑定属性
URCWebInterfaceBlueprintLibrary::RebindProperties(PresetId, PropertyIds, NewOwner);

// 获取所有同类型 Actor 的属性值（JSON）
TMap<AActor*, FString> Values = URCWebInterfaceBlueprintLibrary::GetValuesOfActorsByClass(
    APointLight::StaticClass());
```

### 进阶用法 — WebApp 状态管理

```cpp
// FRemoteControlWebInterfaceProcess 有以下状态
enum class EStatus : uint8
{
    Stopped,   // 未运行
    Launching, // 正在启动（首次启动会下载/编译 WebApp）
    Running,   // 正在运行
    Error      // 出错
};
```

### 进阶用法 — Widget 元数据系统

在 Remote Control Panel 中，每个暴露的实体可以配置 Web Widget 类型：

| 属性类型 | 可选 Widget |
|---|---|
| 数值 (int, float) | Slider, Dial |
| Boolean | Toggle |
| 文本 (Text, Name, String) | Text |
| Byte (Enum) | Dropdown |
| Enum | Dropdown |
| FVector / FVector2D / FRotator | Vector, Joystick, Sliders, Dials |
| FColor / FLinearColor / FVector4 | Color Picker, Mini Color Picker |
| Object | Asset |
| Function | Button |

## Demo 示例

### 最小使用流程

**前置条件：**
- 安装 Node.js (>=14，推荐 16.x)
- 启用 RemoteControl 和 RemoteControlWebInterface 插件

**步骤：**

1. **创建 Remote Control Preset：**
   - 在 Content Browser 右键 → Miscellaneous → Remote Control Preset
   - 打开 Remote Control Panel（Window → Virtual Production → Remote Control Panel）

2. **暴露属性：**
   - 在场景中选择一个 Actor（如 Directional Light）
   - 在 Details 面板中右键要暴露的属性 → Expose to Remote Control

3. **访问 Web 界面：**
   - Remote Control Panel 顶部会出现 "Web App" 按钮
   - 点击按钮会在浏览器中打开 Web 界面（默认地址: `http://127.0.0.1:30000/?preset={PresetId}`）
   - 也可以直接在浏览器中输入地址访问

4. **自定义 Widget：**
   - 在 Remote Control Panel 中选择暴露的属性
   - 在 Metadata 区域可以设置 Widget 类型和 Description
   - Web 界面会自动使用对应的 Widget 展示

### 控制台命令

```
RCWebInterface Start     // 启动 WebApp
RCWebInterface Stop      // 停止 WebApp
RCWebInterface Restart   // 重启 WebApp
```

### 命令行参数

```
-RCWebInterfaceEnable    // 在非编辑器模式下启用 Web 界面（默认仅编辑器启用）
-RCWebInterfaceDisable   // 禁止 WebApp 自动启动
```

### CVar

```
RCWebInterface.AutoStart = 1   // 设为 0 可禁用自动启动
```

## 模块依赖

从 Build.cs 的 PublicDependencyModuleNames 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `Slate` / `SlateCore` | UI 框架（编辑器面板扩展） |
| `Projects` | 插件管理 |
| `RemoteControl` | Remote Control 核心模块 |
| `Sockets` | 网络通信 |
| `WebRemoteControl` | Web Remote Control HTTP/WebSocket 服务器 |
| `WebSocketNetworking` | WebSocket 网络层 |

编辑器额外依赖：`RemoteControlCommon`、`RemoteControlLogic`、`RemoteControlUI`、`PropertyEditor`、`UnrealEd`

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-09-24 | `f38bb00` | 增加 Web Interface 版本号以强制重建（配合 CL 44879464 的改动） |
| 2025-09-23 | `75deeec` | 修复 macOS 上 Start 脚本中 bin 目录 PATH 不是绝对路径导致后续脚本失败的问题 |
| 2025-09-23 | `f8be513` | 修复 Web 进程 shared_ptr 被全局多播委托按值捕获的问题 |

### 维护评价

- **创建时间**：2020-12-11，已超过 5 年
- **活跃度**：近期（2025年9月）仍有实质性 bug 修复，属于**活跃维护**状态
- **稳定性**：代码成熟，近期更新主要是 bug 修复和平台兼容性改进
- **依赖要求**：需要 Node.js 运行时，首次启动会自动下载 Node.js 16.17.0 并编译 WebApp
- **平台支持**：Mac、Win64、Linux
- **推荐度**：✅ 推荐使用，这是 Epic 官方虚拟制片工具链的标准组件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControlWebInterface)
- [RemoteControl 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl)
- [WebRemoteControl 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl/Source/WebRemoteControl)
