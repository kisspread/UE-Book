# DMX Protocol

> DMX Protocols implementation

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXProtocol` (Runtime), `DMXProtocolArtNet` (Runtime), `DMXProtocolSACN` (Runtime), `DMXProtocolEditor` (Editor), `DMXProtocolBlueprintGraph` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2019-11-19 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXProtocol) | |

## 用途

DMX Protocol 插件为 Unreal Engine 提供了完整的 DMX (Digital Multiplex) 协议支持。DMX 是一种用于控制舞台灯光、特效设备等的标准通信协议。该插件的核心目的是在虚拟制片 (Virtual Production) 工作流中，实现 Unreal Engine 与外部 DMX 设备（如灯光控制台、LED 灯具、特效机器）之间的实时、双向数据通信。

它解决了以下问题：
1.  **协议集成**：将行业标准的 DMX 协议栈（包括 ArtNet 和 sACN）集成到引擎中。
2.  **数据映射**：提供将 Unreal Engine 中的灯光参数（如颜色、强度、位置）映射到 DMX 通道的功能。
3.  **实时控制**：允许从 Unreal Engine 发送 DMX 数据来控制物理设备，或接收来自 DMX 控制台的数据来驱动引擎内的对象。
4.  **蓝图支持**：通过蓝图节点暴露核心功能，使设计师和技术美术无需编写 C++ 代码即可实现 DMX 交互。

## 使用场景

-   **虚拟制片 (Virtual Production)**：在 LED 墙拍摄中，使用 Unreal Engine 的灯光系统通过 DMX 协议精确控制实际 LED 面板的亮度和颜色，实现与虚拟场景的无缝匹配。
-   **现场活动与演出**：在演唱会、剧院演出中，使用 Unreal Engine 作为主控，通过 DMX 控制舞台灯光、烟雾机、激光灯等设备，实现复杂的灯光秀编程。
-   **建筑可视化与主题公园**：在大型沉浸式体验项目中，通过 DMX 协议将 Unreal Engine 中的交互事件与实体灯光、机械装置同步。
-   **灯光控制台集成**：将 Unreal Engine 作为一个高级的“灯光控制台”，通过 ArtNet 或 sACN 网络控制整个灯光网络。

## 蓝图用法

该插件通过 `DMXProtocolBlueprintGraph` 模块为蓝图提供了自定义的图表引脚和节点，以简化 DMX 数据的处理。

### 核心节点

由于提供的头文件主要涉及编辑器图表扩展，核心的 DMX 协议蓝图节点（如发送/接收数据、设置通道值）通常定义在 `DMXProtocol` 运行时模块中。基于插件架构，可推断出以下关键蓝图功能类别：

| 节点类别 | 说明 | 所在类 (推断) |
|---|---|---|
| **DMX 协议管理** | 创建、获取、销毁 DMX 协议实例（如 ArtNet, sACN）。 | `UDMXProtocolBlueprintFunctionLibrary` |
| **发送 DMX 数据** | 向指定的 DMX Universe 发送通道数据。 | `UDMXProtocolBlueprintFunctionLibrary` |
| **接收 DMX 数据** | 监听并处理来自 DMX Universe 的数据更新事件。 | `UDMXProtocolBlueprintFunctionLibrary` |
| **DMX 引脚** | 在蓝图图表中用于表示 DMX 地址、Universe ID 或通道数据的自定义引脚。 | `FDMXProtocolGraphPanelPinFactory` |

### 使用示例（蓝图描述）

1.  **初始化协议**：在游戏模式或 Actor 的 `BeginPlay` 事件中，调用“Create DMX Protocol”节点，选择协议类型（如 ArtNet）并配置网络参数（如 IP 地址、端口）。
2.  **发送数据**：当需要控制灯光时，调用“Send DMX Data”节点。将目标 Universe ID 和包含通道值的数组（例如，红、绿、蓝、亮度）连接到该节点。数组索引对应 DMX 通道号（1-512）。
3.  **接收数据**：创建一个自定义事件，并将其绑定到“On DMX Data Received”委托。在该事件中，可以解析传入的通道数据数组，并用于驱动场景中灯光组件的属性或触发其他逻辑。

## C++ 用法

### 头文件引入

```cpp
// 核心协议接口
#include "DMXProtocolModule.h"
#include "DMXProtocolTypes.h"

// 特定协议实现（例如 ArtNet）
#include "DMXProtocolArtNet.h"

// 蓝图图表扩展（仅编辑器）
#include "DMXProtocolBlueprintGraphModule.h"
```

### 基本用法

以下示例展示了如何在 C++ 中初始化一个 ArtNet 协议实例并发送简单的 DMX 数据。

```cpp
// 来源: 基于 DMXProtocol 模块架构推断
#include "DMXProtocolModule.h"
#include "Interfaces/IDMXProtocol.h"

void AMyActor::InitializeDMX()
{
    // 获取 DMX 协议模块
    IDMXProtocolModule& DMXProtocolModule = FModuleManager::GetModuleChecked<IDMXProtocolModule>(TEXT("DMXProtocol"));

    // 创建一个 ArtNet 协议实例
    TSharedPtr<IDMXProtocol> ArtNetProtocol = DMXProtocolModule.CreateProtocol(TEXT("ArtNet"));
    if (ArtNetProtocol.IsValid())
    {
        // 配置并启动协议
        ArtNetProtocol->Start();

        // 准备要发送的 DMX 数据 (Universe 1, 通道 1-3 设置为 RGB)
        FDMXBufferPtr DMXBuffer = MakeShared<FDMXBuffer>();
        DMXBuffer->SetChannelValue(1, 255); // 通道1: 红色
        DMXBuffer->SetChannelValue(2, 0);   // 通道2: 绿色
        DMXBuffer->SetChannelValue(3, 0);   // 通道3: 蓝色

        // 发送数据到 Universe 1
        ArtNetProtocol->SendDMXBuffer(1, DMXBuffer);
    }
}
```

### 进阶用法

监听并处理来自外部控制台的 DMX 数据。

```cpp
// 来源: 基于 DMXProtocol 事件系统推断
#include "DMXProtocolModule.h"
#include "Interfaces/IDMXProtocol.h"

class FDMXDataListener : public IDMXProtocolListener
{
public:
    virtual void OnDMXDataReceived(uint16 UniverseID, const FDMXBufferPtr& DMXBuffer) override
    {
        // 处理接收到的 DMX 数据
        // 例如，读取通道1的值并设置灯光强度
        uint8 Intensity = DMXBuffer->GetChannelValue(1);
        UE_LOG(LogTemp, Log, TEXT("Received DMX on Universe %d, Channel 1: %d"), UniverseID, Intensity);
    }
};

void AMyActor::StartListening()
{
    IDMXProtocolModule& DMXProtocolModule = FModuleManager::GetModuleChecked<IDMXProtocolModule>(TEXT("DMXProtocol"));
    TSharedPtr<IDMXProtocol> Protocol = DMXProtocolModule.GetProtocol(TEXT("ArtNet"));

    if (Protocol.IsValid())
    {
        // 创建并注册监听器
        TSharedPtr<FDMXDataListener> Listener = MakeShared<FDMXDataListener>();
        Protocol->AddListener(Listener);
    }
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何设置 DMX 协议并发送数据。

**MyDMXActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Interfaces/IDMXProtocol.h"
#include "MyDMXActor.generated.h"

UCLASS()
class MYPROJECT_API AMyDMXActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDMXActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    TSharedPtr<IDMXProtocol> DMXProtocol;
};
```

**MyDMXActor.cpp**
```cpp
#include "MyDMXActor.h"
#include "DMXProtocolModule.h"

AMyDMXActor::AMyDMXActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyDMXActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取协议模块并创建 ArtNet 实例
    IDMXProtocolModule& Module = FModuleManager::GetModuleChecked<IDMXProtocolModule>(TEXT("DMXProtocol"));
    DMXProtocol = Module.CreateProtocol(TEXT("ArtNet"));

    if (DMXProtocol.IsValid())
    {
        DMXProtocol->Start();

        // 发送初始数据
        FDMXBufferPtr Buffer = MakeShared<FDMXBuffer>();
        Buffer->SetChannelValue(1, 128); // 通道1设为128
        DMXProtocol->SendDMXBuffer(1, Buffer);
    }
}

void AMyDMXActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (DMXProtocol.IsValid())
    {
        DMXProtocol->Stop();
        DMXProtocol.Reset();
    }
    Super::EndPlay(EndPlayReason);
}
```

**Build.cs 依赖**
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "DMXProtocol" // 关键依赖
});
```

## 模块依赖

从模块结构和功能推断，使用该插件的核心功能需要以下依赖：

| 模块 | 用途 |
|---|---|
| `DMXProtocol` | 核心运行时模块，提供协议接口、缓冲区管理和基础功能。 |
| `DMXProtocolArtNet` | ArtNet 协议的具体实现。 |
| `DMXProtocolSACN` | sACN (E1.31) 协议的具体实现。 |
| `DMXProtocolBlueprintGraph` | 提供蓝图图表中的自定义引脚和节点，用于编辑器扩展。 |
| `DMXProtocolEditor` | 提供编辑器内的自定义资产、细节面板和工具。 |

## 维护状态

### 近期更新

1.  **`ed12aec9a262` (2023-10-27)**: `DMX: Remove any uses of FORCEINLINE, replace with inline where appropriate`
    *   **解读**: 代码风格和编译优化调整，将 `FORCEINLINE` 替换为更合适的 `inline`。这是维护性更新，不影响功能。
2.  **`6248f8d412ba` (2023-10-26)**: `Replacing legacy EditorStyle calls with AppStyle`
    *   **解读**: 跟随引擎 API 更新，将已弃用的 `EditorStyle` 调用替换为新的 `AppStyle`。这是为了保持与最新引擎版本的兼容性。
3.  **`d64cf417281e` (2023-10-25)**: `AssetRegistry includes (Engine Plugins): change #include "AssetData.h" -> #include "AssetRegistry/AssetData.h"`
    *   **解读**: 更新头文件包含路径，以适应引擎中 AssetRegistry 模块的重构。同样是维护性更新。

### 维护评价

-   **创建时间**: 该插件于 2019 年底创建，已有约 5 年历史。
-   **最近更新频率**: 最近的提交集中在 2023 年 10 月，均为跟随引擎主版本的维护性更新（API 替换、头文件路径调整），没有新功能或重大 bug 修复。
-   **活跃度**: 插件功能已相对成熟和稳定。近期的更新表明它仍在被维护以确保与最新引擎版本的兼容性，但并非处于活跃的功能开发阶段。
-   **推荐使用**: **推荐使用**。作为 Epic Games 官方提供的虚拟制作核心组件之一，该插件是 UE 中进行 DMX 集成的标准且可靠的选择。其架构清晰，支持主流协议（ArtNet, sACN），并提供了完善的蓝图和 C++ 接口。尽管近期没有新功能，但其稳定性和官方支持是其主要优势。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXProtocol)
-   [官方文档]() (无直接链接，可参考 UE 官方虚拟制作文档中关于 DMX 的部分)