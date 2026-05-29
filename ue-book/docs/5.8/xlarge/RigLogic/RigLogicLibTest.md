# RigLogic Plugin

> RigLogic Plugin for Facial Animation

| 属性 | 值 |
|---|---|
| 中文名 | 面部动画系统 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（DNA 面部动画资产） |
| 模块 | `RigLogicLib` (Runtime), `RigLogicModule` (Runtime), `RigLogicEditor` (Runtime), `RigLogicDeveloper` (Runtime), `RigLogicLibTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-07-20 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/RigLogic) | |

## 用途

RigLogic 是一个高性能的**面部动画运行时系统**，用于驱动基于 DNA（Digital Normalized Anatomy）文件格式的角色面部动画。DNA 文件是由 DAZ 3D 或 Reallusion 等工具生成的面部骨骼和表情数据的标准化容器。

该插件解决的核心问题是：如何在运行时高效地将少量 GUI 控制值（如"微笑"、"眨眼"）映射到大量的面部骨骼变换和变形目标（BlendShape）输出。它实现了多层级的求值管线：

1. **GUI → Raw 控制映射**：将用户友好的 GUI 控制名称转换为内部 Raw 控制值
2. **条件表（ConditionalTable）**：应用分段线性映射曲线（from/to/slope/cut）
3. **PSD（Pose Space Deformation）**：控制值之间的二次相关项
4. **BPCM 求值器**：Block-Packed Column Major 矩阵乘法，计算骨骼关节变换（支持欧拉角和四元数旋转）
5. **BlendShape 求值器**：从输入控制值映射到变形目标权重
6. **ML 行为**：通过神经网络推断额外的控制值
7. **RBF 求解器**：径向基函数求解器，处理多姿态间的平滑插值
8. **Twist/Swing**：扭转和摆动骨骼修正

所有计算都支持多级 LOD（Level of Detail），可根据角色与摄像机的距离动态降低计算精度以优化性能。

## 使用场景

- 你需要驱动 MetaHuman 或其他基于 DNA 格式的角色面部动画 → 使用 RigLogic
- 你需要在运行时高效地计算数百个 BlendShape 和骨骼变换 → 使用 RigLogic 的优化 BPCM 和 BlendShape 求值器
- 你需要支持 ML 推断的面部动画混合 → 使用 RigLogic 的 MachineLearnedBehavior 模块
- 你需要处理面部动画的 RBF 姿态插值 → 使用 RigLogic 的 RBF 求解器
- 你需要支持多 LOD 级别的面部动画 → RigLogic 原生支持每个求值器的 LOD 约束

## 蓝图用法

RigLogic 主要通过 `AnimNode_RigLogic` 动画节点集成到动画蓝图中，大部分功能在内部运行时求值，不直接暴露为蓝图可调用节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| AnimNode_RigLogic | 动画蓝图节点，自动从 DNA 数据求值面部动画 | `FAnimNode_RigLogic` |
| RigRuntimeContext | 运行时上下文，持有求值器实例和配置 | `URigRuntimeContext` |

### 使用示例（蓝图描述）

在动画蓝图中：
1. 在 AnimGraph 中添加 **RigLogic** 节点
2. 连接到骨骼网格体组件，指定包含 DNA 数据的 SkeletalMesh
3. RigLogic 节点会在每帧自动求值所有面部控制值，并将结果写入骨骼变换和 BlendShape 权重
4. 通过 ControlRig 或其他控制源驱动 GUI 控制曲线，RigLogic 会自动完成映射和求值

## C++ 用法

RigLogic 的核心库是纯 C++ 实现（`RigLogicLib` 模块），不依赖 UE，可独立使用。

### 头文件引入

```cpp
#include "riglogic/RigLogic.h"
#include "dna/Reader.h"
#include "dna/Writer.h"
#include "dna/BinaryStreamReader.h"
```

### 基本用法

从测试用例中提取的核心使用模式：

```cpp
// 加载 DNA 二进制文件（来源：Private/dnatests/TestBinaryStreamWriter.h）
#include "dna/BinaryStreamReader.h"
#include "dna/BinaryStreamWriter.h"
#include "trio/MemoryStream.h"
#include "pma/DefaultMemoryResource.h"

// 创建内存流和读取器
pma::DefaultMemoryResource memRes;
auto stream = pma::makeScoped<trio::MemoryStream>();
auto writer = dna::BinaryStreamWriter::create(stream.get(), &memRes);
auto reader = dna::BinaryStreamReader::create(stream.get(), {}, &memRes);

// 使用 writer 填充 DNA 数据，然后用 reader 读取
// reader 提供完整的 DNA 数据访问接口
std::uint16_t lodCount = reader->getLODCount();
std::uint16_t jointCount = reader->getJointCount();
std::uint16_t blendShapeCount = reader->getBlendShapeChannelCount();
```

### 进阶用法

从测试数据结构分析得出的求值器创建模式：

```cpp
// BPCM 关节求值器（来源：Private/rltests/joints/bpcm/BPCMFixturesBlock4.h）
// BPCM 使用 Block-Packed Column Major 格式优化矩阵乘法
// 数据以 float 或 half-float 存储，支持 SIMD 加速

// 关节求值需要以下数据：
// 1. jointGroupValues: 分组的稀疏矩阵（每组独立的行数×列数）
// 2. inputIndices: 输入控制的索引
// 3. outputIndices: 输出关节的索引
// 4. LOD 约束：每个关节组有自己的 LOD 范围

// 中性关节姿态（neutral pose）作为偏移量叠加：
// neutralJointTranslationXs/Ys/Zs
// neutralJointRotationXs/Ys/Zs

// BlendShape 求值器（来源：Private/rltests/blendshapes/BlendShapeFixtures.h）
// 输入：15个控制值 → 输出：10个变形目标权重
// 通过 inputIndices 和 outputIndices 映射稀疏输入到密集输出

// ML 行为求值器（来源：Private/rltests/ml/cpu/FixturesBlock4.h）
// 神经网络层级结构：
//   - 每个网络有多层（layer），每层有权重矩阵、偏置向量和激活函数
//   - 支持 float 和 half-float 精度
//   - 操作类型：MLP（多层感知机）、WeightedSum、Gather、Scatter
//   - 支持操作间的依赖关系和 LOD 约束

// RBF 求解器（来源：Private/rltests/rbf/cpu/RBFFixtures.h）
// 每个求解器配置：
//   - solverType: 求解器类型
//   - solverRadius: 影响半径
//   - solverDistanceMethod: 距离计算方法
//   - solverFunctionType: 核函数类型
//   - solverNormalizeMethod: 归一化方法
//   - poseScales: 每个姿态的缩放因子
```

## Demo 示例

以下是一个基于 DNA Reader 接口读取面部动画数据的最小示例：

```cpp
// MyFaceAnimComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyFaceAnimComponent.generated.h"

UCLASS(ClassGroup=(Animation), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyFaceAnimComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyFaceAnimComponent();

    // 从 DNA 流初始化求值器
    UFUNCTION(BlueprintCallable, Category="Face Animation")
    bool InitializeFromDNA(class UAnimSequence* DNASource);

    // 设置 GUI 控制值并求值
    UFUNCTION(BlueprintCallable, Category="Face Animation")
    void SetControlValue(const FName& ControlName, float Value);

protected:
    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction) override;

private:
    // 缓存的控制值
    TMap<FName, float> ControlValues;
    bool bInitialized = false;
};
```

```cpp
// MyFaceAnimComponent.cpp
#include "MyFaceAnimComponent.h"
#include "dna/BinaryStreamReader.h"
#include "trio/FileStream.h"
#include "pma/DefaultMemoryResource.h"

UMyFaceAnimComponent::UMyFaceAnimComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
}

bool UMyFaceAnimComponent::InitializeFromDNA(UAnimSequence* DNASource)
{
    // 实际项目中需通过 RigLogicModule 的公共接口获取 DNA Reader
    // 此处展示 DNA Reader API 的使用方式

    pma::DefaultMemoryResource memRes;

    // 读取 DNA 文件示例
    auto stream = pma::makeScoped<trio::FileStream>(
        "path/to/character.dna", trio::AccessMode::Read, trio::OpenMode::Binary);
    auto* reader = dna::BinaryStreamReader::create(stream.get(), {}, &memRes);

    // 获取角色信息
    const auto name = reader->getName();
    const auto lodCount = reader->getLODCount();
    const auto guiControlCount = reader->getGUIControlCount();

    UE_LOG(LogTemp, Log, TEXT("Loaded DNA: %hs, LODs: %d, Controls: %d"),
        name.data(), lodCount, guiControlCount);

    // 读取 GUI 控制名称
    for (uint16_t i = 0; i < guiControlCount; ++i)
    {
        auto controlName = reader->getGUIControlName(i);
        ControlValues.Add(FName(UTF8_TO_TCHAR(controlName.data())), 0.0f);
    }

    // 读取关节和变形目标信息
    const auto jointCount = reader->getJointCount();
    const auto blendShapeCount = reader->getBlendShapeChannelCount();

    UE_LOG(LogTemp, Log, TEXT("Joints: %d, BlendShapes: %d"),
        jointCount, blendShapeCount);

    // 清理
    dna::BinaryStreamReader::destroy(reader);

    bInitialized = true;
    return true;
}

void UMyFaceAnimComponent::SetControlValue(const FName& ControlName, float Value)
{
    if (ControlValues.Contains(ControlName))
    {
        ControlValues[ControlName] = FMath::Clamp(Value, 0.0f, 1.0f);
    }
}

void UMyFaceAnimComponent::BeginPlay()
{
    Super::BeginPlay();
}

void UMyFaceAnimComponent::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (!bInitialized)
    {
        return;
    }

    // 在实际使用中，控制值会被传递给 AnimNode_RigLogic 进行求值
    // RigLogic 内部会完成 GUI→Raw 映射、条件表、PSD、BPCM、BlendShape 等全部管线
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RigLogicLib` | RigLogic 核心 C++ 库，DNA 解析和求值器实现 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体工具函数 |
| `MessageLog` | 编辑器消息日志 |
| `RHI` / `RenderCore` | 渲染硬件接口（用于 GPU 加速） |
| `AssetRegistry` | 资产注册表访问 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `de0806c7` | Fix RigLogic NaN output from TwistSwing/RBF when ControlAttributeCurves overwrites driver-joint quat | 修复 ControlAttributeCurves 覆盖驱动关节四元数时 TwistSwing/RBF 输出 NaN 的问题 |
| 2026-05-13 | `52da7ee0` | Fix quaternion joints evaluator test in case no rotation support is compiled in for the zyx sequence | 修复 zyx 旋转序列未编译支持时四元数关节求值器测试的问题 |
| 2026-05-13 | `27f94d1b` | Fix RigLogic ML Joints initialization of rotation adapter in the absence of coordinate system conver | 修复缺少坐标系转换时 ML 关节旋转适配器初始化问题 |
| 2026-05-13 | `4b5d4e7d` | Notify dependent AnimNode_RigLogic instances when RigRuntimeContext is reinitialized due to config c | 配置变更导致 RigRuntimeContext 重新初始化时通知依赖的 AnimNode_RigLogic 实例 |
| 2026-05-12 | `9006d42c` | Implement identical integration tests for all three RigLogic runtime integrations, AnimNode RigLogic | 为三种 RigLogic 运行时集成实现一致的集成测试 |

### 维护评价

RigLogic 插件处于**活跃维护**状态。最近的更新集中在：

- **Bug 修复**：修复了 TwistSwing/RBF 求值器在特定边界条件下的 NaN 输出问题，以及 ML 关节旋转适配器的初始化问题
- **测试完善**：新增了三种运行时集成方式的统一集成测试
- **架构改进**：实现了配置变更时的依赖通知机制

该插件由 Epic Games 官方维护，是 MetaHuman 角色系统的底层核心组件。代码质量高，包含大量的自动化测试（覆盖 DNA 多版本读写、BPCM 求值、ML 神经网络推断、RBF 求解、BlendShape、ConditionalTable 等所有子系统）。**强烈推荐使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/RigLogic)
- [官方文档]()（未提供）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/RigLogic/Source/RigLogicLibTest)