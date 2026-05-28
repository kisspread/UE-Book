# Deformer Graph

> Editor for creating GPU mesh deformation graphs

| 属性 | 值 |
|---|---|
| 中文名 | 变形器图 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `OptimusCore` (Runtime), `OptimusDeveloper` (Runtime), `OptimusEditor` (Runtime), `OptimusSettings` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DeformerGraph) | |

## 用途

DeformerGraph 是一个基于 GPU 的网格变形图编辑器。它允许开发者在编辑器中通过可视化图形界面，使用 HLSL 代码编写自定义变形逻辑，并直接在 GPU 上执行。其核心是 **Optimus 框架**，它将传统的 CPU 驱动的骨骼网格体动画（Skeletal Mesh）替换为 GPU 驱动的计算图，从而可以实现更复杂、更高性能的变形效果，例如程序化布料、肌肉模拟、次级运动和动态细节变形。该插件默认未启用，因为它是一个实验性功能，需要用户手动开启。

## 使用场景

- **程序化角色变形**：为角色创建基于程序化逻辑的肌肉、脂肪或皮肤变形。
- **高性能次级运动**：实现角色头发、尾巴、衣物等次级运动，直接在 GPU 上计算。
- **动态细节调整**：根据距离或性能要求，动态增加或减少网格体细节。
- **复杂材质变形结合**：将变形逻辑与材质逻辑结合，实现更高级的视觉效果。

## 蓝图用法

### 核心节点

由于插件提供的是编辑器工具和运行时计算框架，直接暴露给蓝图的 API 相对较少，主要集中在设置和状态查询。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Is Supported` | 检查当前着色器平台是否支持 DeformerGraph | `Optimus` (命名空间) |
| `Is Enabled` | 检查 DeformerGraph 当前是否启用 | `Optimus` (命名空间) |
| `Get Default Mesh Deformer` | 根据骨骼网格体设置获取默认的网格变形器 | `UOptimusSettings` |

### 使用示例（蓝图描述）

1.  **检查平台支持**：
    在 BeginPlay 或自定义函数中，调用 `Is Supported` 节点，输入当前的着色器平台（通常从 `Get Current Shader Platform` 节点获取），以决定后续是否启用 GPU 变形功能。
2.  **动态切换变形器**：
    通过 `Get Default Mesh Deformer` 节点，可以获取在项目设置中配置的默认变形器，并应用到骨骼网格体组件的 `Mesh Deformer` 属性上。

## C++ 用法

### 头文件引入

```cpp
#include "OptimusSettings.h"
```

### 基本用法

主要通过 `UOptimusSettings` 和 `Optimus` 命名空间中的函数来与系统交互。

```cpp
// 检查当前平台是否支持
EShaderPlatform Platform = GMaxRHIShaderPlatform;
bool bIsSupported = Optimus::IsSupported(Platform);

// 检查功能是否启用
bool bIsEnabled = Optimus::IsEnabled();

// 获取开发者设置
const UOptimusSettings* Settings = GetDefault<UOptimusSettings>();
EOptimusDefaultDeformerMode Mode = Settings->DefaultMode;
```
*来源：Engine/Plugins/Animation/DeformerGraph/Source/OptimusSettings/Public/OptimusSettings.h*

### 进阶用法

监听设置变更，以便在运行时响应配置更改。

```cpp
// 在你的模块中注册监听
void FMyModule::StartupModule()
{
    if (UOptimusSettings::OnSettingsChange.IsBound())
    {
        // 已经有绑定，检查逻辑
    }
    UOptimusSettings::OnSettingsChange.AddRaw(this, &FMyModule::OnDeformerGraphSettingsChanged);
}

void FMyModule::OnDeformerGraphSettingsChanged(const UOptimusSettings* Settings)
{
    // 重新缓存默认变形器或更新UI
}

void FMyModule::ShutdownModule()
{
    UOptimusSettings::OnSettingsChange.RemoveAll(this);
}
```
*参考实现：Engine/Plugins/Animation/DeformerGraph/Source/OptimusSettings/Private/OptimusSettingsModule.cpp*

## Demo 示例

由于 DeformerGraph 主要是一个编辑器工具和运行时计算框架，其“示例”通常是通过编辑器创建资产。一个最小的可运行 C++ 示例需要连接到计算框架，这通常涉及创建 `UOptimusDeformer` 资产和 `UOptimusDeformerInstance`。

```cpp
// MyDeformerComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyDeformerComponent.generated.h"

class UMeshDeformer;
class UMeshDeformerInstance;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyDeformerComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyDeformerComponent();

    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

    /** 应用指定的网格变形器 */
    UFUNCTION(BlueprintCallable, Category = "Deformer")
    void ApplyMeshDeformer(UMeshDeformer* InDeformer);

private:
    UPROPERTY(Transient)
    TObjectPtr<UMeshDeformerInstance> MeshDeformerInstance;
};
```

```cpp
// MyDeformerComponent.cpp
#include "MyDeformerComponent.h"
#include "MeshDeformer.h"
#include "MeshDeformerInstance.h"
#include "Components/SkeletalMeshComponent.h"

UMyDeformerComponent::UMyDeformerComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
}

void UMyDeformerComponent::BeginPlay()
{
    Super::BeginPlay();
    // 可以在这里初始化一个默认的变形器
}

void UMyDeformerComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    // 驱动变形器实例的计算
    if (MeshDeformerInstance)
    {
        MeshDeformerInstance->Execute(DeltaTime);
    }
}

void UMyDeformerComponent::ApplyMeshDeformer(UMeshDeformer* InDeformer)
{
    if (!InDeformer)
    {
        return;
    }

    // 为当前组件创建并初始化变形器实例
    if (USkeletalMeshComponent* SkeletalMeshComp = GetOwner()->FindComponentByClass<USkeletalMeshComponent>())
    {
        MeshDeformerInstance = InDeformer->CreateInstance(SkeletalMeshComp);
        if (MeshDeformerInstance)
        {
            MeshDeformerInstance->Initialize();
        }
    }
}
```

## 模块依赖

从各模块的 Build.cs 中提取的独特依赖。

| 模块 | 用途 |
|---|---|
| `ComputeFramework` | GPU 计算框架，提供计算图和调度能力 |
| `MeshDescription` | 处理网格描述和拓扑信息 |
| `RHI` | 渲染硬件接口，用于访问 GPU 资源 |
| `ShaderCore` | 着色器编译和管理核心 |
| `RenderCore` | 渲染核心，用于数据缓冲区管理 |
| `Projects` | 用于获取模块路径和插件信息 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `43a2c5ff` | Deformer Graph: programmatic component resolver | 为变形器图添加了程序化的组件解析功能 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数的警告 |
| 2026-04-24 | `59214322` | [ComputeFramework + Optimus] Added Per-kernel output mask for data interfaces... | 为数据接口添加了逐内核的输出掩码功能 |
| 2026-04-16 | `004f9e11` | Deformer Graph: ability to look for secondary bindings in parent actors... | 支持在父级 Actor 中查找次级绑定 |
| 2026-04-14 | `909e5b5b` | [Deformer Graph] Move Mark Deformed to PostSubmit and GetReadableOutputBuffer to Gather dispatch data... | 优化了计算调度流程，移动了相关函数调用 |

### 维护评价

- **活跃维护**：该插件处于非常活跃的开发状态。从 2026 年至今，每月都有多次提交，内容涉及功能增强（如程序化组件解析、次级绑定）、性能优化（如计算调度优化）和稳定性修复（如编译警告）。
- **实验性功能**：`.uplugin` 中明确标记为 `IsBetaVersion: true`，且默认未启用，表明它仍被视为实验性功能，API 和行为未来可能变化。
- **推荐程度**：**强烈推荐**给有高级骨骼网格体变形需求且愿意尝试前沿功能的开发者。尽管是实验性的，但由 Epic Games 官方积极维护，是实现高性能 GPU 变形的首选方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DeformerGraph)
- [官方文档](https://docs.unrealengine.com) (待 Epic 更新)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DeformerGraph/Tests) (推测路径)