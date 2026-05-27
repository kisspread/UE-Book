# Audio Definition Model (ADM)

> Currently only supports output spatialized using WASAPI aggregate output channels and spatial ADM information transmitted using Open Sound Control (OSC).

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | false (Installed: false, IsExperimentalVersion: true) |
| 包含内容 | true |
| 模块 | ADMSpatialization (Runtime, Win64 only) |
| 创建时间 | 2024-11-19 |
| 年龄标签 | 🆕 (~1.5 年) |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/ADM) | |

## 用途

ADM Plugin 实现了 **Audio Definition Model (ADM)** 标准的空间音频输出。它是一个空间化（Spatialization）插件，将 UE5 的音源位置信息通过 **OSC (Open Sound Control)** 协议发送给外部 ADM 兼容渲染器（如 SPARTA、IEM 等），同时通过 **WASAPI 聚合设备（Aggregate Device）** 将每个音源的原始音频发送到独立的 Direct Output 通道。

简单来说：UE5 负责游戏逻辑和音源管理，ADM 负责空间渲染——这个插件是两者之间的桥梁。

**核心工作流程：**
1. 每个音源被分配一个 Direct Output 通道（通过 WASAPI Aggregate Device）
2. 每帧计算音源相对听者的位置，转换为 ADM 坐标系
3. 通过 OSC 消息将位置信息发送到外部 ADM 渲染器
4. 外部渲染器根据位置信息对 Direct Output 音频进行空间化处理

**坐标系转换：** 
```
UNREAL                    ADM-OSC
 Z                          Z
 |    X                     |    Y
 |   /                      |   /
 |  /                       |  /
 | /                        | /
 |/_______________Y         |/_______________X
```

## 使用场景

- 你在做一个沉浸式音频装置，需要将音源空间位置信息输出到外部专业音频渲染器（如 SPARTA、DearVR、IEM 插件等）
- 你需要利用 WASAPI Aggregate Device 将多个音源分别输出到不同的物理音频通道
- 你在做 Ambisonics 或基于对象的空间音频（Object-Based Audio），需要符合 ADM-OSC 标准
- 你的音频管线需要 UE5 作为音源管理前端，后端由专业音频工具做空间渲染

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Send IP Address` | 设置 ADM OSC 消息的目标 IP 地址和端口 | `UADMEngineSubsystem` |

### 使用示例（蓝图描述）

1. 获取 `ADMEngineSubsystem`（通过 Get Engine Subsystem 节点选择 `ADMEngineSubsystem` 类型）
2. 连接 `Set Send IP Address` 节点，填入目标渲染器的 IP（如 `"127.0.0.1"`）和端口（如 `4001`）
3. 之后所有空间化音源的位置信息会自动通过 OSC 发送到该地址

> **注意**：此 Subsystem 仅在运行时可用，不支持在 Construction Script 中调用。

## C++ 用法

### 头文件引入

```cpp
#include "ADMSpatialization.h"          // FADMClient, FADMSpatialization, UADMEngineSubsystem
#include "ADMSpatializationModule.h"    // FModule
#include "ADMSpatializationSettings.h"  // UADMSpatializationSettings (项目设置)
```

### 基本用法：通过 Subsystem 设置 OSC 目标地址

```cpp
// 获取 ADM Engine Subsystem
UADMEngineSubsystem* ADMSubsystem = GEngine->GetEngineSubsystem<UADMEngineSubsystem>();
if (ADMSubsystem)
{
    // 设置 OSC 发送目标
    ADMSubsystem->SetSendIPAddress(TEXT("127.0.0.1"), 4001);
}
```

### 进阶用法：直接操作 FADMClient

```cpp
using namespace UE::ADM::Spatialization;

// 手动创建 OSC 端点
FIPv4Endpoint Endpoint;
FIPv4Endpoint::Parse(TEXT("192.168.1.100:4001"), Endpoint);

// 创建 ADM Client（第二个参数为对象索引偏移，通常为 Bed 通道数）
FADMClient Client(Endpoint, 0);

// 初始化对象（参数为对象索引，是否使用笛卡尔坐标）
Client.InitObjectIndex(0, true);

// 设置音源位置（UE 坐标系，内部自动转换为 ADM 坐标系）
Client.SetPosition(0, FVector(100.0f, 200.0f, 50.0f));
```

### 进阶用法：访问 Factory 和 Spatialization 实例

```cpp
// 获取 ADMSpatialization 模块
FModule& Module = FModuleManager::Get().LoadModuleChecked<FModule>("ADMSpatialization");
FADMSpatializationFactory& Factory = Module.GetFactory();

// 获取或设置 OSC 发送端点
FIPv4Endpoint CurrentEndpoint = Factory.GetSendIPEndpoint();

// 检查是否为 External Send 模式
bool bIsExternalSend = Factory.IsExternalSend(); // 总是返回 true
```

## Demo 示例

### 最小可运行示例

**Build.cs 依赖：**
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "OSC",
    "ADMSpatialization"
});
```

**ADMDemo.h：**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ADMDemo.generated.h"

UCLASS()
class AADMDemo : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "ADM")
    FString TargetIP = TEXT("127.0.0.1");

    UPROPERTY(EditAnywhere, Category = "ADM")
    int32 TargetPort = 4001;
};
```

**ADMDemo.cpp：**
```cpp
#include "ADMDemo.h"
#include "ADMSpatialization.h"

void AADMDemo::BeginPlay()
{
    Super::BeginPlay();

    // 获取 ADM Subsystem 并设置 OSC 目标
    if (UADMEngineSubsystem* ADMSubsystem = GEngine->GetEngineSubsystem<UADMEngineSubsystem>())
    {
        ADMSubsystem->SetSendIPAddress(TargetIP, TargetPort);
        UE_LOG(LogTemp, Log, TEXT("ADM: OSC target set to %s:%d"), *TargetIP, TargetPort);
    }
}
```

## 项目设置

ADM Plugin 通过 `UADMSpatializationSettings`（继承自 `UDeveloperSettings`）提供项目级配置，可在 **Project Settings → Plugins → ADM Spatialization Settings** 中找到：

| 设置项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `IPAddress` | FString | 空 | OSC 目标 IP 地址，设置后启用 ADM 空间化 |
| `IPPort` | int32 | 4001 | OSC 目标端口（ADM-OSC 标准默认 4001） |

编辑器中修改 IP/端口后会自动重新连接 ADM OSC Client。

## 控制台变量

| CVar | 默认值 | 说明 |
|---|---|---|
| `au.ADM.Spatialization.OSCSendEndpoint` | 空 | 覆盖项目设置中的 OSC 发送端点（格式：`127.0.0.1:8000`） |
| `au.ADM.Spatialization.OSCPositionAddressOffset` | -1 | 覆盖 OSC 位置地址中的对象 ID 偏移（-1 使用系统默认） |

## OSC 消息格式

该插件遵循 **ADM-OSC** 规范，发送以下类型的 OSC 消息：

| OSC 地址 | 参数 | 说明 |
|---|---|---|
| `/adm/obj/{id}/config/cartesian` | int (0 或 1) | 初始化对象，设置坐标系为笛卡尔 |
| `/adm/obj/{id}/xyz` | float x, y, z | 设置对象位置（ADM 坐标系） |

其中 `{id}` = 通道索引 + 对象索引偏移（默认为 Bed 通道数）。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioExtensions` | 音频扩展接口（IAudioSpatialization 等） |
| `Core` | 核心库 |
| `CoreUObject` | UObject 系统 |
| `DeveloperSettings` | 项目设置基础设施 |
| `Engine` | 引擎核心 |
| `Networking` | 网络功能 |
| `OSC` | Open Sound Control 协议支持 |
| `AudioMixerCore` | 音频混音器核心（私有依赖） |
| `AudioMixer` | 音频混音器（私有依赖） |
| `SignalProcessing` | 信号处理（私有依赖） |

**Plugin 依赖：** OSC Plugin（在 .uplugin 中声明）

## 平台限制

**仅支持 Win64**。原因是该插件依赖 WASAPI Aggregate Device 进行多通道 Direct Output，这是 Windows 特有的音频 API。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-04-22 | `52e6e467` | Aggregate device enumeration and editor UI for audio device selection | 新增聚合设备枚举和编辑器 UI，允许在编辑器中选择音频设备 |
| 2025-01-28 | `b71c100e` | Fix incorrect UE to ADM-OSC coordinate translation | 修复坐标系转换 bug（UE → ADM-OSC 的 X/Y 交换问题） |
| 2025-01-15 | `31aeb609` | Add direct out channel map which maps source IDs to channel/object IDs to ADM plugin | 新增 Source ID 到通道/对象 ID 的映射机制 |

### 维护评价

- **创建时间**：2024-11-19，约 1.5 年历史
- **最后更新**：2025-04-22，约 1 年前
- **状态**：**实验性**（`IsExperimentalVersion: true`，`EnabledByDefault: false`）
- **活跃度**：中等。2025 年初有功能新增和 bug 修复，之后无更新
- **已知限制**：仅支持 Win64；仅支持单声道（Mono）音源输入；依赖 WASAPI Aggregate Device
- **推荐**：如果你的空间音频管线基于 ADM-OSC 标准，这是一个有价值的实验性插件。但因为它标记为 Experimental 且仅限 Win64，不建议在生产环境中依赖它。适合原型验证和专业音频装置项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ADM)
- [ADM-OSC 规范](https://adm.ebu.io/)（EBU ADM 标准）
- 官方文档：无（.uplugin 中 DocsURL 为空）
