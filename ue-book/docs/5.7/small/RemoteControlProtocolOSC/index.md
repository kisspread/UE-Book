# Remote Control Protocol OSC

> Allows interactions between OSC and RemoteControl API.

| 属性 | 值 |
|---|---|
| 分类 | Messaging |
| 默认启用 | 是 |
| 包含内容 | 否 |
| 模块 | RemoteControlProtocolOSC (Runtime) |
| 创建时间 | 2021-04-08 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControlProtocolOSC) | |

## 用途

RemoteControlProtocolOSC 是 UE5 **Remote Control** 系统的协议扩展插件，为 Remote Control API 提供 **OSC (Open Sound Control)** 传输层支持。

Remote Control 系统允许你通过网络协议远程控制引擎中的任意属性（如 Actor 的位置、旋转、材质参数等）。该插件将 OSC 协议作为传输绑定，使外部 OSC 客户端（如 TouchOSC、Max/MSP、TouchDesigner、QLab 等虚拟制作常用工具）可以通过 OSC 消息驱动 Unreal 内部的属性变化。

**为什么存在：** Remote Control 本身是协议无关的抽象层，需要具体的协议插件来处理网络通信。OSC 是虚拟制作和现场演出行业中事实标准的控制协议，该插件填补了 OSC 协议与 Remote Control API 之间的桥接。

## 使用场景

- **虚拟制作 (Virtual Production)**：在 LED Volume 拍摄中，灯光师通过 TouchOSC 控制面板实时调整 Unreal 场景中的灯光参数
- **现场演出**：演出控制台（如 QLab）通过 OSC 消息触发 Unreal 中的场景切换或特效参数变化
- **多软件联动**：TouchDesigner / Max/MSP 等创意编程工具通过 OSC 驱动 Unreal 中的视觉效果
- **自研控制面板**：开发团队用自定义 OSC 客户端远程调试和控制引擎参数

## 蓝图用法

该插件没有暴露 BlueprintCallable 函数。所有功能通过 **Remote Control Panel** 编辑器 UI 和 **Project Settings** 配置面板操作。

### 配置步骤

1. **启用插件**：Edit → Plugins → 搜索 "Remote Control Protocol OSC" → 启用（需同时启用 Remote Control 和 OSC 插件）
2. **配置 OSC 服务器**：Project Settings → Plugins → Remote Control OSC Protocol
   - `ServersSettings`：可配置多个 OSC 服务器，每个指定 `ServerAddress`（格式 `IP:Port`，默认 `127.0.0.1:8001`）
3. **绑定属性**：打开 Remote Control Panel（Window → Virtual Production → Remote Control）
   - 暴露要控制的属性到 Remote Control Preset
   - 在协议绑定列表中选择 "OSC" 协议
   - 点击 "Awaiting" 按钮进入自动绑定模式
   - 从 OSC 客户端发送一条消息，插件会自动捕获 OSC 地址并完成绑定
4. **运行时**：OSC 客户端发送消息到对应地址，消息中的 float 值会驱动绑定的属性

### 自动绑定 (Auto Binding)

编辑器中有一个便捷的自动绑定流程：在 Remote Control Panel 中将某个属性的 OSC 协议设为 "Awaiting" 状态后，只需从外部 OSC 客户端发送一条消息，插件会自动将该消息的 OSC 地址（如 `/light/intensity`）绑定到该属性，无需手动输入地址。

## C++ 用法

该插件主要是协议桥接实现，用户通常不直接在 C++ 中调用。但如果你需要扩展或自定义 Remote Control 协议行为，以下信息有用。

### 头文件引入

```cpp
#include "RemoteControlProtocolOSC.h"
#include "RemoteControlProtocolOSCSettings.h"
```

### 核心类

```cpp
// OSC 协议实体 —— 存储单个属性绑定的 OSC 地址信息
struct FRemoteControlOSCProtocolEntity : public FRemoteControlProtocolEntity
{
    // OSC 地址，格式: "/Container1/Container2/Method"
    FName PathName;

    // 范围输入模板 (0.0 ~ 1.0)，用于范围映射绑定
    float RangeInputTemplate = 0.0f;
};

// OSC 协议实现 —— 管理所有 OSC 绑定和消息分发
class FRemoteControlProtocolOSC : public FRemoteControlProtocol
{
public:
    static const FName ProtocolName; // = "OSC"

    // 绑定/解绑协议实体
    virtual void Bind(FRemoteControlProtocolEntityPtr InPtr) override;
    virtual void Unbind(FRemoteControlProtocolEntityPtr InPtr) override;
    virtual void UnbindAll() override;

    // OSC 消息接收回调
    void OSCReceivedMessageEvent(const FOSCMessage& Message, const FString& IPAddress, uint16 Port);
};
```

### 消息处理流程

当 OSC 消息到达时，插件执行以下步骤：

1. 从 `FOSCMessage` 提取 `FOSCAddress` 路径
2. （仅编辑器）检查是否有 "Awaiting" 状态的属性，执行自动绑定
3. 使用 `UOSCManager::GetAllFloats()` 提取消息中所有 float 值
4. 在 `Bindings` 映射中查找匹配的 `PathName`
5. 对每个匹配的绑定，通过 `QueueValue()` 将 float 值传递给 Remote Control 系统

**注意：** 该插件仅处理 OSC 消息中的 float 类型参数。其他 OSC 数据类型（int、string、blob 等）会被忽略。

### 服务器配置

OSC 服务器通过 `URemoteControlProtocolOSCSettings` 管理，支持多个服务器实例：

```cpp
// 服务器设置存储在 Project Settings (Config = Engine)
UCLASS(Config = Engine, DefaultConfig)
class URemoteControlProtocolOSCSettings : public UObject
{
    // 可配置多个 OSC 服务器
    UPROPERTY(Config, EditAnywhere, Category = OSC)
    TArray<FRemoteControlOSCServerSettings> ServersSettings;
};

// 每个服务器的配置
struct FRemoteControlOSCServerSettings
{
    // IP:Port 格式，默认 "127.0.0.1:8001"
    FString ServerAddress;

    // 运行时的 OSC Server 实例（自动创建）
    TStrongObjectPtr<UOSCServer> OSCServer;
};
```

## Demo 示例

### 最小工作流程

以下是一个完整的端到端使用流程（纯编辑器操作 + 外部 OSC 客户端）：

**Unreal 侧：**

```
1. 启用插件: RemoteControlProtocolOSC, RemoteControl, OSC
2. Project Settings → Plugins → Remote Control OSC Protocol
   → ServersSettings[0].ServerAddress = "127.0.0.1:9000"
3. 打开 Remote Control Panel
4. 暴露一个 Actor 的 Float 属性（如 Point Light 的 Intensity）
5. 在该属性的协议绑定中选择 OSC，设为 Awaiting
```

**外部 OSC 客户端侧（如 Python + python-osc）：**

```python
from pythonosc.udp_client import SimpleUDPClient

client = SimpleUDPClient("127.0.0.1", 9000)
client.send_message("/light/intensity", 5000.0)  # 自动绑定并设置值
```

### Build.cs 依赖

如果你想在自己的模块中依赖该插件的类型：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
});
PrivateDependencyModuleNames.AddRange(new string[] {
    "OSC",
    "RemoteControl",
    "RemoteControlProtocol",
    "RemoteControlProtocolOSC",
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 引擎核心 |
| `CoreUObject` | UObject 系统 |
| `Networking` | 网络底层支持 |
| `OSC` | OSC 协议实现（消息、地址、服务器） |
| `RemoteControl` | Remote Control 核心框架 |
| `RemoteControlProtocol` | 协议抽象基类 |
| `InputCore` | (仅编辑器) 输入系统 |
| `RemoteControlProtocolWidgets` | (仅编辑器) 协议绑定 UI 组件 |
| `Settings` | (仅编辑器) Project Settings 注册 |

### 依赖的插件

| 插件 | 用途 |
|---|---|
| `RemoteControl` | Remote Control 核心功能 |
| `OSC` | OSC 协议底层实现 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-09-23 | `df329aa` | 移除 motion design 插件的 beta 标签（涉及该插件的元数据变更） |
| 2025-07-24 | `cfcacc2` | 处理无效或空的 OSC 协议实体，增加安全性检查 |
| 2023-01-16 | `bbc37aa` | IWYU 更新，减少不必要的头文件包含 |

### 维护评价

- **年龄**：约 5 年（2021-04 创建）
- **活跃度**：**维护中** — 最近一次功能性更新在 2025-07（null 安全检查），说明仍在被关注
- **代码规模**：极小（5 个源文件），作为协议桥接插件属于正常
- **稳定性**：功能简单且成熟，不太需要频繁更新
- **已知限制**：
  - 仅处理 OSC float 类型参数，不支持 int/string/blob
  - 自动绑定仅在编辑器中可用（WITH_EDITOR）
  - 服务器地址格式固定为 `IP:Port` 字符串

**推荐使用**：如果你的虚拟制作管线使用 OSC 协议，该插件是必选。它是 Epic 官方维护的 Remote Control 协议扩展，与 Remote Control 系统深度集成，稳定可靠。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControlProtocolOSC)
- [Remote Control 文档](https://docs.unrealengine.com/5.0/en-US/remote-control-for-unreal-engine/)（Remote Control 系统整体文档）
- [OSC 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/OSC)（底层 OSC 协议实现）
