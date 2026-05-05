# Deformer Graph

> Editor for creating GPU mesh deformation graphs

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `OptimusSettings` (Runtime), `OptimusCore` (Runtime), `OptimusDeveloper` (UncookedOnly), `OptimusEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/DeformerGraph) | |

## 用途

Deformer Graph（内部代号 **Optimus**）是一个基于节点图的 GPU 网格变形编辑器。它允许开发者和美术通过可视化图编辑器创建自定义的 GPU 变形管线，对骨骼网格体（Skeletal Mesh）进行运行时变形处理。

与传统的 CPU 端 Morph Target 或 AnimBP 变形不同，Deformer Graph 将变形逻辑编译为 GPU Compute Shader，利用 ComputeFramework 在 GPU 上并行执行，性能远优于 CPU 方案。典型应用场景包括：

- **肌肉系统**：基于骨骼驱动的肌肉膨胀/收缩模拟
- **布料/软体**：GPU 加速的次级运动模拟
- **程序化变形**：风力、波浪、碰撞响应等实时效果
- **自定义蒙皮**：替换或增强默认的骨骼蒙皮算法

插件默认禁用（`EnabledByDefault=false`），且标记为 Beta（`IsBetaVersion=true`），需要在项目设置中手动启用。

## 使用场景

- 你需要为角色实现高性能的 GPU 肌肉变形系统 → 用 Deformer Graph
- 你需要在运行时对骨骼网格体进行程序化变形（风力、涟漪等）→ 用 Deformer Graph
- 你需要替换默认蒙皮管线，加入自定义计算步骤 → 用 Deformer Graph
- 你需要一个可视化工具来调试和迭代 GPU 变形逻辑 → 用 Deformer Graph 编辑器

## 蓝图用法

### 核心节点

由于 OptimusCore 模块的详细头文件未在本次分析范围内，以下为基于 Settings 模块和插件架构推断的核心交互点：

| 节点 | 说明 | 所在类 |
|---|---|---|
| 设置默认变形器模式 | 控制骨骼网格体是否自动应用默认变形器 | `UOptimusSettings` |
| 设置默认变形器资产 | 指定项目级别的默认 OptimusDeformer 资产 | `UOptimusSettings` |
| 设置默认重计算切线变形器 | 指定需要重计算切线时使用的变形器 | `UOptimusSettings` |

### 使用示例（蓝图描述）

Deformer Graph 的主要工作流不在蓝图中，而是在编辑器的图编辑器中完成：

1. **创建变形器资产**：在 Content Browser 右键 → Animation → Deformer Graph，创建 `OptimusDeformer` 资产
2. **编辑变形图**：双击打开图编辑器，添加数据接口（如骨骼数据、顶点数据）、计算内核（Kernel）和连接节点
3. **应用到网格体**：在 Skeletal Mesh Component 的 Details 面板中，设置 `Mesh Deformer` 属性为创建的变形器资产
4. **项目级默认设置**：在 Project Settings → DeformerGraph 中配置默认变形器模式和默认资产

## C++ 用法

### 头文件引入

```cpp
#include "OptimusSettings.h"
```

### 基本用法 — 查询 DeformerGraph 支持状态

```cpp
#include "OptimusSettings.h"

// 检查当前平台是否支持 DeformerGraph
bool bSupported = Optimus::IsSupported(GMaxRHIShaderPlatform);

// 检查 DeformerGraph 是否已启用
bool bEnabled = Optimus::IsEnabled();

// 检查资产验证是否启用
bool bValidationEnabled = Optimus::IsAssetValidationEnabled();
```

### 基本用法 — 读取项目设置

```cpp
#include "OptimusSettings.h"

// 获取项目设置
const UOptimusSettings* Settings = GetDefault<UOptimusSettings>();

// 检查默认变形器模式
switch (Settings->DefaultMode)
{
case EOptimusDefaultDeformerMode::Never:
    // 不应用默认变形器
    break;
case EOptimusDefaultDeformerMode::OptIn:
    // 仅在请求时应用
    break;
case EOptimusDefaultDeformerMode::Always:
    // 始终应用默认变形器
    break;
}

// 获取默认变形器资产（软引用，需异步加载）
TSoftObjectPtr<UMeshDeformer> DefaultDeformer = Settings->DefaultDeformer;
```

### 进阶用法 — 监听设置变更

```cpp
#include "OptimusSettings.h"

// 在编辑器中监听 DeformerGraph 设置变更
#if WITH_EDITOR
UOptimusSettings::OnSettingsChange.AddLambda(
    [](const UOptimusSettings* InSettings)
    {
        // 设置已变更，更新相关系统
        UE_LOG(LogTemp, Log, TEXT("DeformerGraph settings updated. DefaultMode: %d"),
            static_cast<int32>(InSettings->DefaultMode));
    });
#endif
```

## Demo 示例

以下示例展示如何在运行时组件中查询 DeformerGraph 配置并决定是否应用变形器：

```cpp
// MyMeshComponent.h
#pragma once

#include "Components/SkeletalMeshComponent.h"
#include "MyMeshComponent.generated.h"

UCLASS()
class UMyMeshComponent : public USkeletalMeshComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
};
```

```cpp
// MyMeshComponent.cpp
#include "MyMeshComponent.h"
#include "OptimusSettings.h"

void UMyMeshComponent::BeginPlay()
{
    Super::BeginPlay();

    const UOptimusSettings* Settings = GetDefault<UOptimusSettings>();

    // 如果项目配置为始终应用默认变形器，且当前组件没有指定变形器
    if (Settings->DefaultMode == EOptimusDefaultDeformerMode::Always
        && GetMeshDeformer() == nullptr)
    {
        // 加载并应用默认变形器
        UMeshDeformer* Deformer = Settings->DefaultDeformer.LoadSynchronous();
        if (Deformer)
        {
            SetMeshDeformer(Deformer);
        }
    }
}
```

## 模块依赖

### 插件依赖

| 插件 | 用途 |
|---|---|
| `ComputeFramework` | GPU 计算框架，Deformer Graph 的底层执行引擎 |
| `ControlRig` | 控制绑定系统，提供骨骼数据接口 |

### OptimusSettings 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。

### OptimusCore 模块依赖（推断）

| 模块 | 用途 |
|---|---|
| `ComputeFramework` | GPU 计算调度与资源管理 |
| `ControlRig` | 骨骼数据读取与绑定 |

## 子模块文档

本插件为 xlarge 规模（536 个源文件），按模块拆分如下：

| 模块 | 类型 | 说明 | 文档 |
|---|---|---|---|
| `OptimusSettings` | Runtime | 项目级配置（默认变形器模式、默认资产） | 见上方 C++ 用法 |
| `OptimusCore` | Runtime | 核心运行时：变形图数据模型、编译、执行 | 需单独文档 |
| `OptimusDeveloper` | UncookedOnly | 开发者工具：验证、调试辅助 | 需单独文档 |
| `OptimusEditor` | Editor | 图编辑器 UI：节点图编辑、预览、调试 | 需单独文档 |

## 维护状态

### 近期更新

```
- 89df8c170d23 Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar instead of on types.
- f673cbafc6d1 [OptimusDeformer] added validation for optimus deformer to detect when a skinnedmesh does not have half edge buffers
- 92020be176c3 [Backout] - CL40616840 [FYI] jack.cai - backed out half edge buffer validation change
```

### 维护评价

- **状态**：Beta 阶段，仍在积极开发中
- **创建时间**：2022 年 8 月，约 3 年历史
- **活跃度**：持续有功能性更新和 bug 修复，属于 Epic 重点推进的动画系统组件
- **已知限制**：
  - 标记为 Beta（`IsBetaVersion=true`），API 可能发生变化
  - 默认禁用（`EnabledByDefault=false`），需手动启用
  - 依赖 ComputeFramework，部分平台可能不支持
  - 需要 GPU Compute Shader 支持
- **推荐程度**：如果你需要 GPU 加速的网格变形，这是 UE5 官方推荐的方案。虽然仍为 Beta，但已有多个 Epic 内部项目在使用。建议在生产环境中谨慎评估稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/DeformerGraph)
- [官方文档]()（暂无）