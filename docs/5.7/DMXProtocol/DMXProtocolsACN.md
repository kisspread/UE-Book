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
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXProtocol) | |

## 用途

DMX Protocol 插件为 Unreal Engine 的虚拟制片（Virtual Production）工作流提供了完整的 DMX512 协议框架。DMX512 是舞台灯光和演出控制行业的标准通信协议，用于控制灯具、LED 面板、烟雾机等舞台设备。

该插件的核心价值在于：

- **统一的协议抽象层**：通过 `IDMXProtocolFactory` 工厂模式和 `IDMXProtocol` 接口，将不同 DMX 传输协议（ArtNet、sACN）封装为可互换的实现，上层代码无需关心底层传输细节
- **两种主流协议支持**：内置 ArtNet（Artistic Licence 的私有协议，广泛用于小型演出）和 sACN（streaming ACN，E1.31 标准，大型演出和安装场景的行业标准）
- **蓝图集成**：通过 `DMXProtocolBlueprintGraph` 模块提供蓝图节点，让灯光设计师和非程序员也能在编辑器中配置和调试 DMX 数据流
- **编辑器工具**：提供 DMX 协议配置界面，管理 Universe（DMX 宇宙，每个宇宙包含 512 个通道）

插件采用 `PreDefault` 加载阶段，确保在其他依赖 DMX 的模块（如 DMXFixture、DMXPixelMapping）之前完成协议注册。

## 使用场景

- 你在搭建虚拟制片 LED Volume 摄影棚，需要通过 DMX 控制 LED 墙面的像素映射 → 使用 DMX Protocol + DMXPixelMapping
- 你在做实时灯光演出预可视化（previz），需要模拟 ArtNet 灯光控制台 → 使用 DMXProtocolArtNet 模块
- 你需要在大型场馆安装中通过 sACN 协议控制数千个 DMX 通道 → 使用 DMXProtocolSACN 模块
- 你在蓝图中需要发送/接收 DMX 数据来驱动灯光效果 → 使用 DMXProtocolBlueprintGraph 提供的蓝图节点
- 你需要通过控制台命令快速测试 DMX 输出 → 使用内置的 `DMX.SACN.SendDMX` 等控制台命令

## 蓝图用法

`DMXProtocolBlueprintGraph` 模块（UncookedOnly 类型）为蓝图系统提供自定义节点支持。基于插件架构，核心蓝图功能通过 DMXProtocol 核心模块暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| DMX 发送相关节点 | 通过指定协议和 Universe 发送 DMX 通道数据 | `UDMXProtocolBlueprintLibrary`（推断） |
| DMX 接收相关节点 | 监听并接收来自 DMX 网络的通道数据 | `UDMXProtocolBlueprintLibrary`（推断） |
| Universe 管理节点 | 创建、查询、销毁 DMX Universe | `UDMXProtocolBlueprintLibrary`（推断） |

> **注意**：由于该插件为 xlarge 规模（148 个源文件），完整的蓝图 API 需要查阅 `DMXProtocolBlueprintGraph` 模块中的 `UK2Node_*` 类和 `DMXProtocol` 核心模块中的 `BlueprintCallable` 函数。建议在编辑器中通过蓝图节点搜索 "DMX" 查看所有可用节点。

### 使用示例（蓝图描述）

1. **发送 DMX 数据**：在蓝图中创建一个 DMX 发送节点 → 设置目标协议（ArtNet 或 sACN）→ 指定 Universe ID（0-64214）→ 设置通道值数组（Channel 0-511，Value 0-255）→ 连接到 Tick 或自定义事件触发发送
2. **接收 DMX 数据**：绑定 DMX 接收回调事件 → 指定监听的 Universe → 在回调中读取通道数据并驱动灯光参数

## C++ 用法

### 头文件引入

```cpp
// 核心协议接口
#include "Interfaces/IDMXProtocol.h"
#include "Interfaces/IDMXProtocolFactory.h"

// sACN 协议特定
#include "DMXProtocolSACNModule.h"

// ArtNet 协议特定
#include "DMXProtocolArtNetModule.h"  // 推断路径
```

### 基本用法

**通过控制台命令发送 sACN DMX 数据**（来源：`DMXProtocolSACNModule.h`）：

```cpp
// 控制台命令格式：
// DMX.SACN.SendDMX [UniverseID] Channel:Value Channel:Value ...
// 示例：DMX.SACN.SendDMX 7 25:156 26:0 27:10 28:15
// 向 Universe 7 发送：通道 25=156, 通道 26=0, 通道 27=10, 通道 28=15

// Universe ID 范围: 0 ~ 64214
// Channel 范围: 0 ~ 511
// Value 范围: 0 ~ 255

// 重置 Universe：
// DMX.SACN.ResetDMXSend 7
```

**协议工厂模式**（来源：`DMXProtocolSACNModule.h`）：

```cpp
// 协议通过工厂模式创建
class FDMXProtocolFactorySACN : public IDMXProtocolFactory
{
public:
    // 根据协议名称创建对应的协议实例
    virtual IDMXProtocolPtr CreateProtocol(const FName& ProtocolName) override;
};

// 模块启动时自动注册到 DMXProtocol 核心模块
void FDMXProtocolSACNModule::StartupModule()
{
    FactorySACN = MakeUnique<FDMXProtocolFactorySACN>();
    // 注册 sACN 协议到全局协议管理器
    // ...
}
```

### 进阶用法

**模块注册机制**（来源：`DMXProtocolSACNModule.h`）：

```cpp
// sACN 模块在启动时通过 RegisterWithProtocolModule 向核心模块注册
// 传入 FDMXProtocolRegistrationParams 数组，包含协议名称、工厂等信息
void FDMXProtocolSACNModule::RegisterWithProtocolModule(
    TArray<FDMXProtocolRegistrationParams>& InOutProtocolRegistrationParamsArray);

// 获取模块单例
FDMXProtocolSACNModule& Module = FDMXProtocolSACNModule::Get();
```

**协议常量**（来源：`DMXProtocolSACNModule.h`）：

```cpp
// 旧版（已废弃 4.27+）：
// static FName const FDMXProtocolSACNModule::NAME_SACN;

// 新版（推荐）：
#include "DMXProtocolSACNConstants.h"
// 使用 DMX_PROTOCOLNAME_SACN 常量
```

## Demo 示例

### 最小 DMX 协议集成示例

**Build.cs**：

```csharp
using UnrealBuildTool;

public class MyDMXGame : ModuleRules
{
    public MyDMXGame(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "DMXProtocol"  // 核心 DMX 协议模块
        });

        // 如果需要特定协议实现：
        // "DMXProtocolArtNet",
        // "DMXProtocolSACN"
    }
}
```

**MyDMXActor.h**：

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Interfaces/IDMXProtocol.h"
#include "MyDMXActor.generated.h"

UCLASS()
class AMyDMXActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDMXActor();

    // 要监听的 Universe ID
    UPROPERTY(EditAnywhere, Category = "DMX")
    int32 UniverseID = 1;

    // DMX 通道数据（512 通道）
    UPROPERTY(VisibleAnywhere, Category = "DMX")
    TArray<uint8> ChannelData;

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    // DMX 数据接收回调
    void OnDMXDataReceived(int32 InUniverseID, const TArray<uint8>& InData);

private:
    TSharedPtr<IDMXProtocol> DMXProtocol;
};
```

**MyDMXActor.cpp**：

```cpp
#include "MyDMXActor.h"
#include "DMXProtocolModule.h"

AMyDMXActor::AMyDMXActor()
{
    PrimaryActorTick.bCanEverTick = false;
    ChannelData.SetNum(512);
}

void AMyDMXActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取 DMX 协议模块并注册 Universe 监听
    // 具体 API 取决于 DMXProtocol 核心模块的公开接口
    // 建议参考 Engine/Plugins/VirtualProduction/DMX/ 下的测试用例
}

void AMyDMXActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 清理 DMX 资源
    Super::EndPlay(EndPlayReason);
}

void AMyDMXActor::OnDMXDataReceived(int32 InUniverseID, const TArray<uint8>& InData)
{
    if (InUniverseID == UniverseID)
    {
        ChannelData = InData;
        // 处理接收到的 DMX 数据...
    }
}
```

> **提示**：完整的 DMX API 使用方式请参考 `Engine/Plugins/VirtualProduction/DMX/` 下的测试用例和 DMX 核心模块的头文件。由于该插件规模较大（xlarge），建议先阅读核心模块 `DMXProtocol` 的接口定义。

## 模块依赖

从各模块 Build.cs 分析，该插件的模块间依赖关系如下：

| 模块 | 用途 |
|---|---|
| `DMXProtocol` | 核心协议框架，定义 `IDMXProtocol`、`IDMXProtocolFactory` 等接口 |
| `DMXProtocolArtNet` | ArtNet 协议实现，依赖 DMXProtocol 核心 |
| `DMXProtocolSACN` | sACN (E1.31) 协议实现，依赖 DMXProtocol 核心 |
| `DMXProtocolEditor` | 编辑器配置 UI，依赖 DMXProtocol 核心 |
| `DMXProtocolBlueprintGraph` | 蓝图节点扩展，依赖 DMXProtocol 核心 |

**使用者需要依赖的模块**：

| 模块 | 用途 |
|---|---|
| `DMXProtocol` | 必须依赖，提供核心接口和协议管理 |
| `DMXProtocolArtNet` | 如需使用 ArtNet 协议则依赖 |
| `DMXProtocolSACN` | 如需使用 sACN 协议则依赖 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 近期 | `ed12aec9a262` | Remove any uses of FORCEINLINE, replace with inline where appropriate | 代码规范化重构，将 `FORCEINLINE` 替换为 `inline`。`FORCEINLINE` 在调试时会导致符号丢失，改用 `inline` 更利于调试且性能影响可忽略 |
| 近期 | `66356fe8dea4` | Improve implementation and robustness of the sACN protocol implementation | sACN 协议实现的健壮性改进，属于功能性更新，说明 sACN 模块仍在积极优化 |
| 近期 | `09ac80358139` | More bool to EAllowShrinking fixes | 跟随引擎 API 变更，`TArray::SetNum()` 的参数从 `bool` 改为 `EAllowShrinking` 枚举 |

### 维护评价

- **创建时间**：2019 年 11 月，约 6 年历史
- **更新频率**：近期有实质性更新（sACN 健壮性改进），说明仍在活跃维护
- **维护状态**：**活跃维护中** — 作为 Virtual Production 工作流的核心组件，Epic 持续投入开发
- **已知限制**：
  - `FDMXProtocolSACNModule::NAME_SACN` 已在 4.27 废弃，需迁移到 `DMX_PROTOCOLNAME_SACN`
  - 插件规模较大（148 个源文件），学习曲线较陡
- **推荐程度**：⭐⭐⭐⭐⭐ 强烈推荐 — 这是 UE5 虚拟制片 DMX 控制的官方实现，功能完整且持续维护

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXProtocol)
- [官方文档]()（暂无）
- [测试用例]()（需在 `Engine/Plugins/VirtualProduction/DMX/` 目录下搜索测试文件）

---

## 子模块文档索引

由于本插件为 xlarge 规模（148 个源文件），按子模块拆分如下：

| 子模块 | 类型 | 说明 |
|---|---|---|
| [DMXProtocol](DMXProtocol-Core.md) | Runtime | 核心协议框架，定义接口和协议管理器 |
| [DMXProtocolArtNet](DMXProtocolArtNet.md) | Runtime | ArtNet 协议实现 |
| [DMXProtocolSACN](DMXProtocolSACN.md) | Runtime | sACN (E1.31) 协议实现 |
| [DMXProtocolEditor](DMXProtocolEditor.md) | Editor | 编辑器配置工具 |
| [DMXProtocolBlueprintGraph](DMXProtocolBlueprintGraph.md) | UncookedOnly | 蓝图节点扩展 |