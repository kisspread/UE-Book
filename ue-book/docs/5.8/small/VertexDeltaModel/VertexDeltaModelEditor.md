# ML Deformer Vertex Delta Model

> Vertex Delta Model for the ML Deformer Framework

| 属性 | 值 |
|---|---|
| 中文名 | 顶点增量模型 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（ML Deformer 模型资产） |
| 模块 | `VertexDeltaModel` (Runtime), `VertexDeltaModelEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-09-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/VertexDeltaModel) | |

## 用途

VertexDeltaModel 是 ML Deformer 框架的一种具体实现模型，用于通过机器学习驱动的顶点偏移（Vertex Delta）来提升骨骼动画的视觉质量。它解决了传统骨骼蒙皮无法精确表现肌肉挤压、布料褶皱等次级动画效果的问题。

该插件的核心工作流程是：

1. **训练阶段**：基于 GeomCache（几何体缓存）资产作为 Ground Truth，通过 NNE（Neural Network Engine）框架训练一个神经网络模型，学习从骨骼姿态到每顶点位置偏移量（Delta）的映射关系
2. **推理阶段**：在运行时对每一帧骨骼姿态，使用训练好的神经网络预测顶点偏移，叠加到基础蒙皮结果上，产生更高质量的网格变形效果

与传统的 Morph Target 方案相比，机器学习方法可以用更小的数据量捕获更复杂的变形关系，特别适合电影级角色动画质量的实时还原。

## 使用场景

- 你有一个高精度的离线动画（如 Maya/Houdini 的肌肉模拟），需要在 UE5 中实时还原接近的效果 → 使用 VertexDeltaModel 训练并部署
- 你的角色有复杂的面部表情系统，Morph Target 数量爆炸 → 用 ML Deformer 压缩为神经网络模型
- 你需要高质量的次级动画（Secondary Motion），但不想在运行时做昂贵的物理模拟 → 离线训练一个 Vertex Delta 模型

## 蓝图用法

该插件的蓝图 API 主要通过 `UVertexDeltaTrainingModel` 暴露，用于自定义训练流程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Train` | 执行训练（需要 Python 实现） | `UVertexDeltaTrainingModel` |

### 训练模型

`UVertexDeltaTrainingModel` 继承自 `UMLDeformerGeomCacheTrainingModel`，其 `Train()` 函数标记为 `BlueprintImplementableEvent`，意味着训练逻辑需要通过 Python 脚本实现。在编辑器中创建 Vertex Delta Model 资产后，可以通过 ML Deformer 编辑器面板触发训练。

### 使用流程

1. 在 Content Browser 中右键 → Animation → ML Deformer Asset，选择 Vertex Delta Model
2. 配置骨骼网格体、GeomCache 资产等基础设置
3. 在 Details 面板中调整训练参数
4. 点击 Train 按钮启动训练（需要 Python ML 环境）
5. 训练完成后，将 ML Deformer Component 附加到角色蓝图中使用

## C++ 用法

该插件主要面向编辑器扩展，运行时通过 ML Deformer 框架统一调度。以下是编辑器端的自定义扩展方式。

### 头文件引入

```cpp
#include "VertexDeltaModel.h"
#include "VertexDeltaEditorModel.h"
#include "VertexDeltaTrainingModel.h"
```

### 基本用法 — 自定义编辑器模型

编辑器模型负责训练和加载神经网络。如果需要扩展编辑器行为，可继承 `FVertexDeltaEditorModel`：

```cpp
// 来源: Public/VertexDeltaEditorModel.h
namespace UE::VertexDeltaModel
{
    using namespace UE::MLDeformer;

    // 获取编辑器模型实例
    static FMLDeformerEditorModel* EditorModel = FVertexDeltaEditorModel::MakeInstance();

    // 获取关联的 VertexDeltaModel 资产
    UVertexDeltaModel* Model = EditorModel->GetVertexDeltaModel();

    // 从 ONNX 文件加载神经网络
    TObjectPtr<UNNEModelData> ModelData = EditorModel->LoadNeuralNetworkFromOnnx(TEXT("/Game/Models/trained_model.onnx"));

    // 执行训练
    ETrainingResult Result = EditorModel->Train();
}
```

### 进阶用法 — 自定义 Details 面板

如果需要为 Vertex Delta Model 添加自定义属性面板，可继承 `FVertexDeltaModelDetails`：

```cpp
// 来源: Public/VertexDeltaModelDetails.h
namespace UE::VertexDeltaModel
{
    // 注册自定义 Details 面板
    class FMyVertexDeltaModelDetails : public FVertexDeltaModelDetails
    {
    public:
        static TSharedRef<IDetailCustomization> MakeInstance()
        {
            return MakeShareable(new FMyVertexDeltaModelDetails());
        }

        void CustomizeDetails(IDetailLayoutBuilder& DetailBuilder) override
        {
            // 先调用父类的定制逻辑
            FVertexDeltaModelDetails::CustomizeDetails(DetailBuilder);

            // 添加自定义属性...
            IDetailCategoryBuilder& MyCategory = DetailBuilder.EditCategory(TEXT("MyCustomSettings"));
            // ...
        }
    };
}
```

## Demo 示例

以下展示如何创建一个自定义的 Vertex Delta 编辑器模型扩展：

### MyVertexDeltaExtension.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "VertexDeltaEditorModel.h"

namespace UE::VertexDeltaModel
{
    /**
     * 自定义 Vertex Delta 编辑器模型扩展
     * 可用于添加自定义的预处理/后处理逻辑
     */
    class FMyVertexDeltaExtension : public FVertexDeltaEditorModel
    {
    public:
        // 工厂方法
        static FMLDeformerEditorModel* MakeInstance()
        {
            return new FMyVertexDeltaExtension();
        }

        // 扩展训练前的检查
        virtual ETrainingResult Train() override
        {
            // 自定义的前置检查
            UVertexDeltaModel* Model = GetVertexDeltaModel();
            if (!Model)
            {
                return ETrainingResult::Failure;
            }

            // 调用原始训练逻辑
            return FVertexDeltaEditorModel::Train();
        }
    };
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MLDeformer` | ML Deformer 核心框架 |
| `MLDeformerFramework` | ML Deformer 运行时框架 |
| `NNE` | 神经网络引擎（Neural Network Engine） |
| `GeometryCache` | 几何体缓存，用于存储 Ground Truth 变形数据 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `1d7ad320` | UE 5.8 Animation deprecation clean up (CL 8/10): MLDeformer | 清理 ML Deformer 相关的废弃代码 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移为新格式 |
| 2026-04-02 | `138d5376` | [Deformer Graph] Multiple fixes for Optimus runtime | 修复 Deformer Graph 和 Optimus 运行时多个问题 |
| 2025-06-25 | `a9573a81` | ComputeFramework: Remove old deprecated functions from compute data providers. | 移除旧的废弃计算数据提供者函数 |
| 2025-06-20 | `35f8ecb8` | PythonFoundationPackages: Move Torch python requirements to separate PythonMLPackages plugin | 将 PyTorch 依赖迁移到独立插件 |

### 维护评价

- **状态**：活跃维护中
- 最近更新集中在 2026 年 4 月，包含代码清理和 bug 修复，说明仍在持续维护
- 作为 ML Deformer 框架的核心模型之一，与主框架保持同步更新
- 仍处于 Beta 阶段（`IsBetaVersion=true`），API 可能在后续版本变化
- 依赖 Python ML 环境（PyTorch 等），需要注意运行时依赖
- **推荐使用**：适合需要高质量次级动画的项目，但需接受 Beta 阶段的潜在 API 变更

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/VertexDeltaModel)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)
- [ML Deformer 主框架源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/MLDeformer)