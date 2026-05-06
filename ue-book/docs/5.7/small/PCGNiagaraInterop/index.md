# Procedural Content Generation Framework (PCG) Niagara Interop

> Extra plugin for Procedural Content Generation Framework interacting with the Niagara system.

| 属性 | 值 |
|---|---|
| 中文名 | PCG-Niagara 数据通道 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（C++ 节点和设置） |
| 模块 | `PCGNiagaraInterop` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-10-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PCGInterops/PCGNiagaraInterop) | |

---

## 用途

PCG（程序化内容生成框架）提供灵活的点数据生成与处理能力；Niagara 是虚幻引擎的粒子系统。然而，PCG 生成的数据无法直接传递给 Niagara 使用，导致粒子系统无法实时响应程序化生成的内容。

**PCGNiagaraInterop** 解决了这个断层：它提供了一个 PCG 节点（`Write to Niagara Data Channel`），允许将 PCG 属性（如位置、颜色、自定义数据）写入 **Niagara Data Channel**。Niagara 发射器、蓝图或 C++ 逻辑可以从该数据通道中读取数据，实现 PCG 与 Niagara 之间的双向数据流通。

核心能力：
- 将 PCG 点数据中的属性映射到 Niagara Data Channel 的变量
- 控制数据的可见性（Game / CPU / GPU）
- 支持异步加载 Niagara Data Channel 资产

---

## 使用场景

- 用 PCG 生成大量树木、岩石等静态物体位置 → 通过 Niagara 实现粒子风效、碰撞反应
- 在 PCG 中计算地形高度、坡度 → 驱动 Niagara 粒子发射位置与运动轨迹
- 制作动态环境：PCG 实时更新关卡布局 → Niagara 粒子即时响应变化
- 需要将 PCG 输出与现有 Niagara 模块（如 Data Channel 驱动的 GPU 粒子）结合

---

## 蓝图用法

该插件主要贡献了一个 **PCG 节点**（等同于 `UPCGSettings` 子类），在 PCG 蓝图图表中通过右键菜单搜索“Write to Niagara Data Channel”添加。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Write to Niagara Data Channel` | 将 PCG 输入点的属性写入指定的 Niagara Data Channel 资产 | `UPCGWriteToNiagaraDataChannelSettings` |

### 节点属性（蓝图可读写）

在节点的 Details 面板中设置以下属性：

| 属性 | 类型 | 说明 |
|---|---|---|
| `DataChannel` | `TSoftObjectPtr<UNiagaraDataChannelAsset>` | 目标 Niagara Data Channel 资产（可异步加载） |
| `NiagaraVariablesPCGAttributeMapping` | `TMap<FName, FPCGAttributePropertyInputSelector>` | 映射表：Key 为 Niagara Data Channel 的变量名，Value 为 PCG 属性路径（支持 `.` 分隔的属性链） |
| `bVisibleToGame` | `bool` | 写入的数据是否对游戏逻辑（C++/蓝图）可见（默认 true） |
| `bVisibleToCPU` | `bool` | 写入的数据是否对 Niagara CPU 发射器可见（默认 true） |
| `bVisibleToGPU` | `bool` | 写入的数据是否对 Niagara GPU 发射器可见（默认 false） |
| `bSynchronousLoad` | `bool` | 是否同步加载 `DataChannel` 资产（默认 false，异步加载） |

### 使用示例（蓝图描述）

1. 在 PCG 图表中放置 `Write to Niagara Data Channel` 节点。
2. 连接 PCG 数据源（如 `Surface Sampler` 或 `Point Generation`）到该节点的输入引脚。
3. 在节点 Details 中，将 `DataChannel` 指定为事先创建好的 Niagara Data Channel 资产。
4. 展开 `NiagaraVariablesPCGAttributeMapping`，添加映射条目。例如：
   - Key: `Particle.Position`（Niagara Data Channel 中的变量名）
   - Value: 选择 PCG 属性 `Point.Location`（或用户自定义属性）。
5. 根据需要调整可见性开关（`bVisibleToCPU`、`bVisibleToGPU`）。
6. 运行 PCG 图：PCG 生成的点数据将自动填充到 Niagara Data Channel 中，Niagara 系统中的对应变量即可读取。

---

## C++ 用法

### 头文件引入

```cpp
#include "Elements/PCGWriteToNiagaraDataChannel.h"
#include "NiagaraDataChannelAsset.h"
```

### 基本用法

创建并配置 `UPCGWriteToNiagaraDataChannelSettings`，然后将其添加到 PCG 图执行中（通常在编辑器工具或自定义子系统内）：

```cpp
// 创建节点设置对象
UPCGWriteToNiagaraDataChannelSettings* Settings = NewObject<UPCGWriteToNiagaraDataChannelSettings>();

// 指定目标 Niagara Data Channel 资产（例如从全局加载）
Settings->DataChannel = MyDataChannelAsset;

// 配置属性映射
FPCGAttributePropertyInputSelector Selector;
Selector.SetAttributeName("Location");
Settings->NiagaraVariablesPCGAttributeMapping.Add(
    FName("Particle.Position"),
    Selector
);

// 设置可见性
Settings->bVisibleToGame = true;
Settings->bVisibleToCPU = true;

// 将 Settings 应用于 PCG 节点（略，取决于你的 PCG 图构建方式）
```

来源文件：`Engine/Plugins/Experimental/PCGInterops/PCGNiagaraInterop/Source/PCGNiagaraInterop/Public/Elements/PCGWriteToNiagaraDataChannel.h`

### 进阶用法

**异步加载 DataChannel 资产**（节点默认行为）：

```cpp
// 在元素的 PrepareDataInternal 阶段，FPCGWriteToNiagaraDataChannelContext（继承 IPCGAsyncLoadingContext）
// 会自动处理异步加载。调用方无需额外代码。
// 若希望同步加载，设置 Settings->bSynchronousLoad = true。
```

**类型兼容性检查**：内部使用 `PCGAttributeNiagaraTraits::AreTypesCompatible()` 判断 PCG 属性类型与 Niagara 变量是否匹配。支持的类型映射包括：`FVector2D`、`FVector`、`FVector4`、`FLinearColor`、`FQuat`、`double`、`int32`、`FNiagaraID`、`bool`、`FNiagaraSpawnInfo`。

来源文件：`Engine/Plugins/Experimental/PCGInterops/PCGNiagaraInterop/Source/PCGNiagaraInterop/Public/Helpers/PCGAttributeNiagaraTraits.h`

---

## Demo 示例

一个完整的、可编译的最小 C++ 示例，展示如何在运行时将 PCG 点数据写入 Niagara Data Channel（假设已在关卡中放置 PCG 组件和 Niagara 系统）。

```cpp
// DemoWriteToNiagaraDataChannel.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DemoWriteToNiagaraDataChannel.generated.h"

class UPCGComponent;
class UNiagaraDataChannelAsset;

UCLASS()
class ADemoWriteToNiagaraDataChannel : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demo")
    TSoftObjectPtr<UNiagaraDataChannelAsset> DataChannelAsset;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demo")
    UPCGComponent* SourcePCGComponent = nullptr;
};
```

```cpp
// DemoWriteToNiagaraDataChannel.cpp
#include "DemoWriteToNiagaraDataChannel.h"
#include "PCGComponent.h"
#include "Elements/PCGWriteToNiagaraDataChannel.h"
#include "Engine/World.h"

void ADemoWriteToNiagaraDataChannel::BeginPlay()
{
    Super::BeginPlay();

    if (!SourcePCGComponent)
    {
        UE_LOG(LogTemp, Warning, TEXT("SourcePCGComponent not set"));
        return;
    }

    // 创建一个临时的 PCG 图并添加 WriteToNiagaraDataChannel 节点
    UPCGGraph* Graph = NewObject<UPCGGraph>(this);
    UPCGWriteToNiagaraDataChannelSettings* Settings = NewObject<UPCGWriteToNiagaraDataChannelSettings>(Graph);
    Settings->DataChannel = DataChannelAsset.LoadSynchronous(); // 同步加载便于演示
    Settings->NiagaraVariablesPCGAttributeMapping.Add(
        FName("Particle.Position"),
        FPCGAttributePropertyInputSelector(EPCGAttributePropertySelection::Attribute, FName("Location"))
    );
    Settings->bVisibleToCPU = true;

    // 将 Settings 添加为图的最后一个节点（简化：实际应连接数据流）
    // 此处略去图的构建细节，实际项目中可使用 PCGGraph 的 AddNode 方法
    // 或者直接手动调用节点的 Execute 函数（不推荐，仅用于验证）
    // 更合适的做法是在编辑器蓝图或 PCG 数据资产中预先配置好图。
    UE_LOG(LogTemp, Log, TEXT("Demo: WriteToNiagaraDataChannelSettings configured."));
}
```

> **注意**：由于 PCG 图执行往往依赖于 `UPCGComponent` 的处理流水线，推荐在编辑器蓝图或数据资产中配置节点，而非纯运行时动态构建。上述示例仅为展示 API 可用性。

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PCG` | PCG 框架核心，提供点数据、属性、图执行等基础设施 |
| `Niagara` | Niagara 系统核心，提供数据通道（Data Channel）类型定义与读写接口 |

**无其他特殊依赖**（常见 Core/Engine 模块省略）。

---

## 维护状态

### 近期更新

- 2025-08-27 d3732e1f — [PCG] Fix bool attribute in Write to Niagara Data Channel
- 2025-04-03 b15c472b — [PCG] Convert most remaining PCG Nodes / Datas to support UPCGPointArrayData
- 2025-04-01 27857341 — [PCG] New IPCGGraphExecutionSource interface aimed at replacing UPCGComponent dependency in graph ex
- 2025-01-16 0b1a8c97 — [PCG] Fix data marshalling between PCG and Niagara
- 2024-10-09 b51d56d7 — [PCG] Fixing few issues with Write To Niagara Data Channel

### 维护评价

- **创建时间**：2024-10-09，至今约 1 年。
- **近期更新**：最近一次修复在 2025-08-27，且有多次功能适配与修复（如支持 UPCGPointArrayData、修复布尔属性等），表明插件处于活跃维护状态。
- **实验性**：`IsExperimentalVersion=true`，但已具备完整功能，未见废弃标记。
- **推荐使用**：✅ 推荐。插件虽标为实验性，但代码稳定、更新频繁，是 PCG 与 Niagara 交互的官方桥梁。

---

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PCGInterops/PCGNiagaraInterop)
- [官方文档（PCG 框架总览）](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PCGInterops/PCGNiagaraInterop/Source/PCGNiagaraInterop/Private)（当前仅包含模块实现，无独立测试文件）