# GeneSplicer Plugin

> GeneSplicer plugin for facial animation

| 属性 | 值 |
|---|---|
| 中文名 | 基因剪接器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GeneSplicerLib` (Runtime), `GeneSplicerLibTest` (Runtime), `GeneSplicerModule` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-10-21 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GeneSplicer) | |

## 用途

GeneSplicer 是一个专为面部动画设计的插件，它作为 Epic Games 的 DNA（数字生物资产）系统与 Unreal Engine 运行时之间的关键桥梁。其核心功能是处理和转换由 DCC 工具（如 Maya）生成的 DNA 资产数据，使其能够高效地被 UE5 的 RigLogic 运行时加载和驱动。

它解决了两个核心问题：
1.  **数据转换与优化**：将复杂的 DNA 文件转换为 UE5 优化的内部数据结构，并支持在运行时进行动态调整和转换。
2.  **运行时驱动**：在游戏运行时，高效地将 DNA 数据加载到内存，并为 RigLogic 驱动器提供数据源，从而驱动骨骼、变形器和蒙皮，实现高质量的实时面部动画。

简而言之，它不是创造面部动画，而是让预计算的高精度面部动画数据能够在游戏引擎中实时、高效地播放。

## 使用场景

-   你正在开发一个使用高保真数字人（如 MetaHuman）的项目，需要在运行时根据游戏逻辑或玩家输入，动态加载、混合或修改其面部动画数据。
-   你的管线使用 DNA 格式作为面部动画的交换标准，需要在引擎中实现对该格式数据的读取、处理和驱动。
-   你需要对已有的 DNA 资产进行运行时优化或转换（例如，坐标系统转换），以适应不同的渲染或物理需求。

## 蓝图用法

GeneSplicer 主要通过其 C++ 库提供核心功能，但 `GeneSplicerModule` 提供了一些封装以供蓝图使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadDNAAsset` | 从指定路径异步加载一个 DNA 资产，并返回一个 `UDNAAsset` 对象。这是大多数工作的起点。 | `UGeneSplicerBPLibrary` |
| `CreateGeneSplicerComponent` | 为指定的 SkeletalMeshComponent 创建并添加一个运行时驱动组件，该组件内部使用 GeneSplicer 来驱动网格。 | `UGeneSplicerBPLibrary` |

### 使用示例（蓝图描述）

1.  **加载并应用DNA资产**：
    -   节点 `Event BeginPlay` 连接到 `LoadDNAAsset` 节点。
    -   设置 `LoadDNAAsset` 的文件路径参数指向你的 `.dna` 文件。
    -   将其输出的 `DNAAsset` 引用存储到一个变量中。
    -   将 `DNAAsset` 变量作为输入，连接到 `CreateGeneSplicerComponent` 节点，并指定要驱动的 `SkeletalMeshComponent`。

2.  **运行时驱动**：
    -   组件创建后，会自动开始加载和处理 DNA 数据。
    -   RigLogic 运行时会消费 GeneSplicer 提供的数据，从而驱动面部网格的动画。

## C++ 用法

### 头文件引入

```cpp
#include "GeneSplicerLib/Public/GeneSplicer.h"
#include "GeneSplicerModule/Public/DNAAsset.h" // 如果使用 UDNAAsset 包装类
```

### 基本用法

加载一个 DNA 文件并获取其数据接口。
*(来源: GeneSplicerLibTest 测试用例)*

```cpp
#include "GeneSplicerLib/Public/GeneSplicer.h"
#include "GeneSplicerLib/Public/StreamReader.h"

// 1. 创建一个 DNA 数据读取器（例如，从文件）
FGeneSplicer::FStreamReader FileReader;
FileReader.Open(TEXT("/Game/Path/To/Your/Model.dna"));
if (!FileReader.IsOpen()) {
    // 处理打开失败
    return;
}

// 2. 创建 GeneSplicer 实例
FGeneSplicer GeneSplicer;
GeneSplicer.LoadFrom(&FileReader);

// 3. 现在可以通过 GeneSplicer 实例访问 DNA 数据
// 例如，获取关节名称
uint16 JointCount = GeneSplicer.GetJointCount();
for (uint16 i = 0; i < JointCount; ++i) {
    const TCHAR* JointName = GeneSplicer.GetJointName(i);
    // 处理关节名
}
```

### 进阶用法

对 DNA 数据进行批量处理（例如，修改关节旋转），然后序列化到新文件。
*(来源: GeneSplicerLibTest 与 DNACalib 测试用例组合)*

```cpp
#include "GeneSplicerLib/Public/GeneSplicer.h"
#include "GeneSplicerLib/Public/StreamWriter.h"
// 假设使用了 DNACalib 库进行修改
#include "DNACalibLib/Public/DNACalib.h"

// 1. 加载原始 DNA
FGeneSplicer OriginalDNA;
OriginalDNA.LoadFrom(/*...*/);

// 2. 使用 DNACalib 创建一个可修改的 DNA 副本
FGeneSplicer MutableDNA = OriginalDNA; // 假设支持复制或移动
FDNACalibDNAAdapter Adapter(&MutableDNA);

// 3. 进行修改 (例如，将所有关节旋转设为零)
FDNACalibSetNeutralJointRotationsCommand Cmd;
Cmd.SetRotationsToZero(); // 设置为零旋转
Adapter.Run(&Cmd);

// 4. 将修改后的 DNA 保存到新文件
FGeneSplicer::FStreamWriter FileWriter;
FileWriter.Open(TEXT("/Game/Path/To/Modified/Model.dna"));
if (FileWriter.IsOpen()) {
    MutableDNA.SaveTo(&FileWriter);
}
```

## Demo 示例

一个加载 DNA 文件并打印关节信息的最小控制台程序示例。

### GeneSplicerDemo.h
```cpp
#pragma once
class FDemo
{
public:
    static void Run();
};
```

### GeneSplicerDemo.cpp
```cpp
#include "GeneSplicerDemo.h"
#include "GeneSplicerLib/Public/GeneSplicer.h"
#include "GeneSplicerLib/Public/StreamReader.h"
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

void FDemo::Run()
{
    // 注意：实际路径需替换为有效的 .dna 文件路径
    const TCHAR* DNAFilePath = TEXT("C:/Models/TestModel.dna");

    FGeneSplicer::FStreamReader Reader;
    Reader.Open(DNAFilePath);
    if (!Reader.IsOpen())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open DNA file: %s"), DNAFilePath);
        return;
    }

    FGeneSplicer Splicer;
    Splicer.LoadFrom(&Reader);

    UE_LOG(LogTemp, Log, TEXT("DNA Data Loaded Successfully."));
    UE_LOG(LogTemp, Log, TEXT("  Joints: %d"), Splicer.GetJointCount());
    UE_LOG(LogTemp, Log, TEXT("  Blend Shapes: %d"), Splicer.GetBlendShapeCount());

    for (uint16 i = 0; i < Splicer.GetJointCount(); ++i)
    {
        UE_LOG(LogTemp, Verbose, TEXT("  Joint [%d]: %s"), i, Splicer.GetJointName(i));
    }
}

// 在某个模块（如 GeneSplicerModule）的启动函数中调用
// void FMyModule::StartupModule()
// {
//     FDemo::Run();
// }
```

## 模块依赖

要在你的项目中使用 GeneSplicer，你的模块需要在 Build.cs 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `GeneSplicerLib` | 核心 DNA 数据处理库，是插件的基础。 |
| `GeneSplicerModule` | 提供与 UE5 集成的运行时功能（如 DNA 资产类、组件）。 |
| `RigLogicLib` | 驱动运行时动画的核心引擎，GeneSplicer 为其提供数据源。 |
| `DNACalibLib` | DNA 数据校准和操作库，用于运行时修改 DNA 数据。 |
| `ControlRig` | 可选依赖，如果需要将 DNA 驱动与 ControlRig 系统集成。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `2f6aa301` | Improve DNA asset load performance and backwards compatible conversion by reducing data copies | 优化DNA资产加载性能和向后兼容转换，减少数据拷贝 |
| 2026-05-12 | `57c5e2c7` | Update DNA and RigLogic to better handle malformed DNA files | 更新DNA和RigLogic以更好地处理格式错误的DNA文件 |
| 2026-05-12 | `0577289d` | Suppress private module include warnings for test modules (RigLogicLibTest, DNACalibLibTest, DNACali | 抑制测试模块的私有模块包含警告 |
| 2026-04-30 | `82833e51` | Fix data-race on per platform DNAConfig access during serialization | 修复序列化期间按平台DNAConfig访问的数据竞争 |
| 2026-04-28 | `0c7a803e` | Implement face-winding conversion in DNA to support arbitrary coordinate systems in UE | 在DNA中实现面法线绕序转换，以支持UE中的任意坐标系 |

### 维护评价

GeneSplicer 是一个相对较新的插件（创建于2024年底），但近期（2026年）有**非常活跃的维护**。
-   **更新频繁**：最近几次提交都集中在2026年4月底至5月中旬，且都是实质性功能改进和关键bug修复。
-   **内容重要**：更新涉及性能优化、鲁棒性提升（处理损坏数据）、跨平台兼容性修复以及新功能（坐标系支持），表明这是一个在持续迭代和优化中的核心组件。
-   **无废弃迹象**：提交信息中未见 deprecated/obsolete 标记。
-   **推荐使用**：尽管它默认未启用（Installed: false），但作为高保真数字人管线的关键环节，它正受到积极维护和改进。对于需要在运行时处理DNA面部动画数据的项目，**强烈推荐启用和使用**。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GeneSplicer)
-   [官方文档]() (暂无)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GeneSplicer/Source/GeneSplicerLibTest)