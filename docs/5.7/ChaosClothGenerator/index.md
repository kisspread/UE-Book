# Chaos Cloth Generator

> Chaos Cloth Data Generator for ML Deformer

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | 是（需手动启用 Experimental 插件） |
| 包含内容 | 是 |
| 模块 | ChaosClothGenerator (Editor) |
| 创建时间 | 2023-08-10 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/ChaosClothGenerator) | |

## 用途

ChaosClothGenerator 是 ML Deformer 系统的训练数据生成工具。它解决的核心问题是：**如何为 ML Deformer 提供高质量的布料模拟训练数据**。

ML Deformer 通过机器学习来近似布料模拟效果，从而在运行时以极低的性能开销实现逼真的布料变形。但训练 ML Deformer 需要大量的"输入骨骼姿态 → 输出布料顶点位置"配对数据。ChaosClothGenerator 正是自动生成这些配对数据的工具：

1. 输入：骨骼网格体 + Chaos 布料资产 + 动画序列
2. 过程：对动画序列的每一帧运行 Chaos 布料物理模拟
3. 输出：包含模拟结果的 GeometryCache，可直接用于 ML Deformer 训练

## 使用场景

- 你有一个角色穿着布料（披风、裙子、斗篷等），想用 ML Deformer 在运行时替代昂贵的布料物理模拟 → 用 ChaosClothGenerator 生成训练数据
- 你已经配置好了 ChaosClothAsset 和对应的 SkeletalMesh，需要批量生成布料模拟结果 → 用 ChaosClothGenerator 的批处理功能
- 你需要调试单帧的布料模拟效果 → 用 ChaosClothGenerator 的 Debug 模式

## 蓝图用法

本插件是纯编辑器工具，不提供 BlueprintCallable 接口。所有操作通过 ML Deformer 编辑器的 GUI 完成。

## C++ 用法

本插件主要通过编辑器 UI 使用，但其核心类也可以在 C++ 中调用。

### 头文件引入

```cpp
#include "ClothGeneratorComponent.h"
#include "ClothGeneratorProperties.h"
#include "ChaosClothGenerator.h"
```

### 核心类

#### UClothGeneratorProperties

配置参数对象，控制生成行为。

```cpp
// 来源: ClothGeneratorProperties.h
UCLASS()
class UClothGeneratorProperties : public UObject
{
    // 输入: MLDeformer 使用的骨骼网格体
    UPROPERTY(EditAnywhere, Category = Input)
    TObjectPtr<USkinnedAsset> SkeletalMeshAsset;

    // 输入: 用于模拟的 Chaos 布料资产（应与骨骼网格体不同）
    UPROPERTY(EditAnywhere, Category = Input)
    TObjectPtr<UChaosClothAsset> ClothAsset;

    // 输入: 训练姿态的动画序列
    UPROPERTY(EditAnywhere, Category = Input)
    TObjectPtr<UAnimSequence> AnimationSequence;

    // 要模拟的帧范围，例如 "0, 2, 5-10, 12-15"，留空则使用所有帧
    UPROPERTY(EditAnywhere, Category = Input)
    FString FramesToSimulate;

    // 输出: 模拟结果的 GeometryCache
    UPROPERTY(EditAnywhere, Category = Output)
    TObjectPtr<UGeometryCache> SimulatedCache;

    // 模拟时间步长（默认 1/30 秒）
    UPROPERTY(EditAnywhere, Category = "Simulation Settings")
    float TimeStep = 1.f / 30;

    // 每帧的模拟步数（默认 200，越大越精确但越慢）
    UPROPERTY(EditAnywhere, Category = "Simulation Settings")
    int32 NumSteps = 200;

    // 并行线程数（默认 1）
    UPROPERTY(EditAnywhere, Category = "Simulation Settings")
    int32 NumThreads = 1;
};
```

#### UClothGeneratorComponent

继承自 `UChaosClothComponent`，用于离线布料模拟。支持通过组件空间变换设置骨骼姿态。

```cpp
// 来源: ClothGeneratorComponent.h
UCLASS()
class UClothGeneratorComponent : public UChaosClothComponent
{
    // 使用组件空间变换设置布料姿态
    void Pose(const TArray<FTransform>& InComponentSpaceTransforms);
};
```

#### FChaosClothGenerator

核心生成逻辑类，继承自 `FTickableEditorObject`，通过编辑器 Tick 驱动异步模拟任务。

```cpp
// 来源: ChaosClothGenerator.h
class FChaosClothGenerator : public FTickableEditorObject
{
    UClothGeneratorProperties& GetProperties() const;
    void RequestAction(EClothGeneratorActions Action);  // StartGenerate
};
```

### 基本用法（编辑器集成）

插件在启动时将自身注册为 ML Deformer 编辑器的 Tools 菜单扩展：

```cpp
// 来源: ChaosClothGeneratorModule.cpp
void FChaosClothGeneratorModule::StartupModule()
{
    // 注册 Tools 菜单项
    UE::MLDeformer::FMLDeformerEditorToolkit::AddToolsMenuExtender(
        CreateToolsMenuExtender());

    // 注册属性面板自定义
    PropertyModule.RegisterCustomClassLayout(
        "ClothGeneratorProperties",
        FOnGetDetailCustomizationInstance::CreateStatic(
            &FClothGeneratorDetails::MakeInstance));
}
```

## 使用流程

### 1. 准备资产

在开始之前，确保你有以下资产：

- **SkeletalMesh**：角色的骨骼网格体（必须是从 FBX 导入的，有 `MeshToImportVertexMap`）
- **ChaosClothAsset**：基于同一个网格体创建的 Chaos 布料资产
- **AnimationSequence**：用于训练的动画序列
- **GeometryCache**：输出资产（可通过 UI 上的 "New" 按钮创建）

> **重要**：SkeletalMeshAsset 和 ClothAsset 必须有相同的顶点数和相同的顶点顺序。插件会在启动时验证这两个资产的一致性。

### 2. 打开 Chaos Cloth Generator 面板

1. 打开 ML Deformer Asset 的编辑器
2. 在菜单栏找到 **Tools** → **Chaos Cloth Generator**
3. 或者在编辑器中打开 **Chaos Cloth Generator** 标签页

### 3. 配置参数

在面板中设置：

| 参数 | 说明 | 建议值 |
|---|---|---|
| SkeletalMeshAsset | MLDeformer 使用的骨骼网格体 | 你的角色骨骼网格体 |
| ClothAsset | Chaos 布料资产 | 基于同一网格体的布料资产 |
| AnimationSequence | 训练动画 | 包含丰富姿态变化的动画 |
| FramesToSimulate | 模拟帧范围 | 留空 = 全部帧；或如 `"0, 5, 10-20"` |
| SimulatedCache | 输出 GeometryCache | 点 "New" 创建 |
| TimeStep | 模拟时间步 | 默认 1/30 |
| NumSteps | 每帧模拟步数 | 200（越大越精确） |
| NumThreads | 并行线程数 | 根据 CPU 核心数调整 |

### 4. 开始生成

点击 **Start Generating** 按钮。生成过程中会显示进度通知，支持取消。

### 5. 调试模式

勾选 **Debug** 复选框可以调试单帧：

- **DebugFrame**：要检查的帧号
- **DebugCache**：调试输出的 GeometryCache
- Debug 模式下会保存每一步的模拟结果（而非仅保存最终结果）
- Debug 模式强制单线程运行

### 6. 使用输出

生成完成后，输出的 GeometryCache 可以直接用于 ML Deformer 的 GeomCache 模型训练。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库（公共依赖） |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `ChaosClothAssetEngine` | Chaos 布料资产引擎 |
| `GeometryCache` | GeometryCache 资产支持 |
| `MeshDescription` | 网格描述数据 |
| `MLDeformerFramework` | ML Deformer 框架 |
| `MLDeformerFrameworkEditor` | ML Deformer 编辑器集成 |
| `PropertyEditor` | 属性面板自定义 |
| `RenderCore` | 渲染核心 |
| `SkeletalMeshDescription` | 骨骼网格描述 |
| `Slate` / `SlateCore` | UI 框架 |
| `UnrealEd` | 编辑器功能 |
| `DataflowSimulation` | 数据流模拟 |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `ChaosClothAsset` | Chaos 布料资产支持 |
| `GeometryCache` | GeometryCache 资产类型 |
| `MLDeformerFramework` | ML Deformer 框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-10-09 | `6550d0c3` | Fix crash in Cloth Generator when there is no skeleton assigned to a cloth asset | 修复了布料资产未分配骨架时的崩溃问题 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 代码质量改进，添加内联生成宏 |
| 2025-04-10 | `130ca170` | Fix unity build error | 修复 Unity 构建错误 |

### 维护评价

- **创建时间**：2023-08-10，约 2.7 年历史
- **实验性状态**：`.uplugin` 中 `IsExperimentalVersion: true`，属于实验性插件
- **最近更新**：2025-10-09，约 7 个月前有 bug 修复
- **维护状态**：**维护中** — 有持续的 bug 修复和代码改进
- **稳定性**：实验性插件，API 和行为可能随版本变化
- **推荐**：适合在 ML Deformer 工作流中使用，但注意其实验性标签，生产环境需谨慎评估

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/ChaosClothGenerator)
- [ML Deformer Framework](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MLDeformer/MLDeformerFramework)
- [Chaos Cloth Asset](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ChaosClothAsset)
