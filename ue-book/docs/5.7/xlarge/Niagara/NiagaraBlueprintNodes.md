# Niagara

> Niagara effect systems.

| 属性 | 值 |
|---|---|
| 中文名 | 尼亚加拉粒子系统 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图节点、编辑器资源、着色器、动画通知等） |
| 模块 | `Niagara` (Runtime), `NiagaraAnimNotifies` (Runtime), `NiagaraBlueprintNodes` (Runtime), `NiagaraCore` (Runtime), `NiagaraEditor` (Runtime), `NiagaraEditorWidgets` (Runtime), `NiagaraShader` (Runtime), `NiagaraVertexFactories` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-16 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara) | |

## 用途

`NiagaraBlueprintNodes` 是 Niagara 插件的一个运行时模块（分类为 Runtime，主要用于编辑器扩展），它提供了一系列**蓝图节点**，使得在蓝图中可以方便地读写 **Niagara Data Channel（NDC）** 数据。

Niagara Data Channel 是 Niagara 系统中一种高效的数据传输通道，允许在 CPU 和 GPU 之间、不同粒子系统之间、以及蓝图中传递结构化数据。该模块生成的蓝图节点封装了 `UNiagaraDataChannelLibrary` 中的函数调用，降低了在蓝图中使用 NDC 的门槛。

**为什么存在？** 如果没有这些自定义蓝图节点，开发者需要手动调用函数库，并处理复杂的数据类型匹配和展开。该模块通过节点扩展，实现了自动类型推断、引脚生成和编译期展开，提升开发效率。

## 使用场景

- **在蓝图中自定义粒子数据通道**：创建、写入或读取与特定粒子系统绑定的数据通道，例如传递位置、颜色、寿命等自定义属性。
- **实现粒子系统间通信**：通过数据通道在不同发射器或系统实例之间交换数据，无需复杂的 CPU 回调。
- **与 Niagara Data Channel 的访问上下文协作**：支持 `FNDCAccessContextInst` 结构体，用于管理数据访问的上下文（如指定发射器索引、粒子索引等），适用于更精细的控制。
- **在 UI 或逻辑蓝图中动态创建/销毁数据**：利用获取元素数量的节点，实时监控数据通道状态。

## 蓝图用法

该模块提供的蓝图节点主要分为三类：
1. **基础读写节点**：直接读写数据通道，使用内联的 `UNiagaraDataChannelAsset` 引用。
2. **带上下文的读写节点**：支持通过动态引脚连接 `FNDCAccessContextInst` 结构体，实现更灵活的数据访问。
3. **上下文操作节点**：创建、设置、获取 `FNDCAccessContextInst` 的成员变量。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Write to Niagara Data Channel` | 将数据写入指定的 Niagara Data Channel | `UK2Node_WriteDataChannel` |
| `Read from Niagara Data Channel` | 从指定的 Niagara Data Channel 读取数据 | `UK2Node_ReadDataChannel` |
| `Write to Niagara Data Channel (With Context)` | 使用 `FNDCAccessContextInst` 上下文写入数据，支持动态通道指定 | `UK2Node_WriteDataChannel_WithContext` |
| `Read from Niagara Data Channel (With Context)` | 使用 `FNDCAccessContextInst` 上下文读取数据，支持动态通道指定 | `UK2Node_ReadDataChannel_WithContext` |
| `Get Data Channel Element Count (With Context)` | 获取指定数据通道的元素数量，使用上下文 | `UK2Node_DataChannelGetNum_WithContext` |
| `Write Single to Data Channel (With Context)` | 单粒子写入（展开为多个变量写入） | `UK2Node_WriteDataChannelSingle_WithContext` |
| `Read Single from Data Channel (With Context)` | 单粒子读取（展开为多个变量读取） | `UK2Node_ReadDataChannelSingle_WithContext` |
| `Make / Break Data Channel Access Context` | 创建或分解 `FNDCAccessContextInst` 结构体 | `UK2Node_DataChannelAccessContextOperation` 的派生节点 |

### 使用示例（蓝图描述）

1. **写入简单数据通道**：
   - 拖入 `Write to Niagara Data Channel` 节点，在细节面板中指定一个 `UNiagaraDataChannelAsset` 资源。
   - 节点会自动生成该数据通道定义的所有变量引脚（如 `Position`、`Color`、`LifeTime`）。
   - 将这些引脚连接到任意数据源，执行时即写入。

2. **使用上下文读取**：
   - 拖入 `Read from Niagara Data Channel (With Context)` 节点。
   - 先在蓝图中创建一个 `FNDCAccessContextInst` 变量（可通过 `Make Data Channel Access Context` 节点构建）。
   - 将上下文变量连接到节点的 `Access Context` 输入引脚。
   - 节点会生成读出的变量引脚，连接至后续逻辑。

3. **动态指定数据通道**：
   - 带上下文节点支持 `SupportsDynamicDataChannel()`，允许将 `UNiagaraDataChannelAsset` 对象通过引脚传入，而非静态绑定，适合运行时切换通道。

## C++ 用法

该模块本身不直接暴露 C++ 运行时 API，其功能通过蓝图编译展开为 `UNiagaraDataChannelLibrary` 中的函数调用。如果你需要在 C++ 中手动调用，请使用 `NiagaraDataChannelFunctionLibrary`。

### 头文件引入

```cpp
#include "NiagaraDataChannelFunctionLibrary.h"
#include "NiagaraDataChannel.h"
```

### 基本用法

以下示例展示了在 C++ 中直接使用 Niagara Data Channel 的常用流程（来源：`NiagaraDataChannelFunctionLibrary.h` 和测试用例）：

```cpp
// 假设有一个 UNiagaraDataChannelAsset* DataChannelAsset
UNiagaraDataChannelAsset* MyChannel = LoadObject<UNiagaraDataChannelAsset>(nullptr, TEXT("/Game/MyDataChannel.MyDataChannel"));

// 写入数据（需要访问上下文）
FNDCAccessContextInst Context;
Context.SystemInstanceID = TargetSystemInstance->GetId();
Context.EmitterIndex = 0;

// 准备要写入的数据（以位置和颜色为例）
FVector WritePosition = FVector(100.0f, 200.0f, 300.0f);
FLinearColor WriteColor = FLinearColor::Red;

// 调用写入函数（具体函数名可能因版本而异，这里根据节点推断）
UNiagaraDataChannelLibrary::WriteToNiagaraDataChannel(MyChannel, Context, WritePosition, WriteColor);
```

### 进阶用法

通过 `UNiagaraDataChannelLibrary` 可以批量操作数据通道，如遍历、查询元素数量等。

## Demo 示例

以下是一个完整的 C++ 类，演示如何在 Actor 中创建并写入 Niagara Data Channel。

**#include "MyNDCWriter.h"**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NiagaraDataChannel.h"
#include "NiagaraDataChannelFunctionLibrary.h"
#include "MyNDCWriter.generated.h"

UCLASS()
class MYPROJECT_API AMyNDCWriter : public AActor
{
    GENERATED_BODY()

public:
    AMyNDCWriter();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "NDC")
    UNiagaraDataChannelAsset* DataChannelAsset;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "NDC")
    FVector WritePosition;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "NDC")
    FLinearColor WriteColor;
};
```

**#include "MyNDCWriter.cpp"**

```cpp
#include "MyNDCWriter.h"

AMyNDCWriter::AMyNDCWriter()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyNDCWriter::BeginPlay()
{
    Super::BeginPlay();

    if (!DataChannelAsset)
    {
        UE_LOG(LogTemp, Warning, TEXT("No DataChannelAsset assigned."));
        return;
    }

    // 创建访问上下文（这里使用默认值）
    FNDCAccessContextInst Context;
    // 实际使用时需要正确设置 SystemInstanceID 等字段

    // 调用库函数写入
    UNiagaraDataChannelLibrary::WriteToNiagaraDataChannel(
        DataChannelAsset,
        Context,
        WritePosition,
        WriteColor
    );
}
```

> **注意**：实际函数签名请参考 `UNiagaraDataChannelLibrary` 的头文件。节点展开时使用的是 `GET_FUNCTION_NAME_CHECKED(..., WriteToNiagaraDataChannel)`，因此运行时库函数名称应为 `WriteToNiagaraDataChannel`（可能返回 `void`）。

## 模块依赖

`NiagaraBlueprintNodes` 的独特依赖（省略标准 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `Niagara` | Niagara 核心运行时模块，提供数据通道定义 |
| `NiagaraCore` | 核心类型和基础定义（如 `FNiagaraTypeDefinition`） |
| `BlueprintGraph` | 提供 `UK2Node_CallFunction` 等蓝图节点基类 |
| `KismetCompiler` | 蓝图编译支持，用于节点展开 |

> 注意：`UnrealEd`、`PropertyEditor` 等编辑器模块是常规依赖，已省略。

## 维护状态

### 近期更新

| 日期 | Commit | 解读 |
|---|---|---|
| 2025-10-22 | `5d0cd83c` | 修复清理过程中的已释放 Niagara 组件访问问题。 |
| 2025-10-22 | `3f549682` | 修复 CPU 更新无数据时 NDC 数据残留的问题。 |
| 2025-10-21 | `6ac05a79` | 添加默认关闭的 workaround，解决内部测试发现的 Niagara 崩溃。 |
| 2025-10-17 | `f6546371` | 修复 GT 和 RT tick 不匹配导致 NDC 数据丢失的问题。 |
| 2025-10-16 | `566219ca` | 撤销某个变更（CL47013072）。 |

### 维护评价

Niagara 作为 UE5 的核心 VFX 系统，维护非常活跃。从近 7 天的日志看，修正了组件清理、数据同步、崩溃等多个问题，且更新频率高（几乎每天）。`NiagaraBlueprintNodes` 作为其中的一个模块，随着 Niagara 整体的迭代得到持续维护。该模块提供了成熟的蓝图节点解决方案，无已知废弃计划，推荐用于所有需要与 Niagara Data Channel 交互的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara)
- [Niagara Data Channel 官方文档](https://docs.unrealengine.com/5.7/API/Plugins/FX/Niagara/NiagaraDataChannel/)（通用参考）
- [Niagara 插件主目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara)