# RigLogic Plugin

> RigLogic Plugin for Facial Animation

| 属性 | 值 |
|---|---|
| 中文名 | 面部动画驱动 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（DNA 资产、示例数据） |
| 模块 | `RigLogicLib` (Runtime), `RigLogicModule` (Runtime), `RigLogicDeveloper` (Runtime), `RigLogicEditor` (Runtime), `RigLogicLibTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-07-20 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/RigLogic) | |

## 用途

RigLogic 是一个基于机器学习的面部动画运行时系统，用于从少量控制曲线驱动高保真度的角色面部网格变形。它通过解析 DNA 文件（MetaHuman 使用的标准格式），建立控制属性与面部关节/蒙皮权重之间的映射关系，从而实现复杂的面部表情动画。

该插件存在的原因：
- **MetaHuman 集成**：作为 MetaHuman 角色的核心动画驱动后端
- **高性能运行时**：提供原生 C++ 实现的 ML 推理引擎，支持实时面部动画
- **标准化数据格式**：统一的 DNA 文件格式，支持跨 DCC 工具的资产迁移

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [RigLogicLib](RigLogicLib.md) | Runtime (C++) | 核心 ML 运行时库，实现 riglogic 算法、DNA 解析、LOD 管理 |
| [RigLogicModule](RigLogicModule.md) | Runtime | UE5 集成层，提供 AnimNode_RigLogic、蓝图 API、资产类型 |
| [RigLogicDeveloper](RigLogicDeveloper.md) | Runtime | 开发者工具模块，提供调试可视化和性能分析 |
| [RigLogicEditor](RigLogicEditor.md) | Runtime | 编辑器扩展，DNA 资产导入、预览和属性编辑 |
| [RigLogicLibTest](RigLogicLibTest.md) | Runtime | RigLogicLib 的自动化测试套件 |

## 使用场景

- **MetaHuman 角色驱动**：使用 MetaHuman Creator 创建的角色需要实时面部动画
- **高保真面部动画**：需要从少量 BlendShape 或关节控制驱动复杂面部变形
- **大规模角色系统**：游戏中有大量对话/表情动画需求，需要高效的 ML 运行时
- **跨平台面部动画**：需要在不同硬件平台上保持一致的面部动画质量
- **DNA 资产工作流**：从 Maya/3ds Max 导出 DNA 文件并集成到 UE5

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Control Attribute Values` | 获取当前控制属性值数组 | `URigLogicModule` |
| `Set Control Attribute Values` | 设置控制属性值驱动面部动画 | `URigLogicModule` |
| `Get Mesh Count` | 获取 DNA 文件中的网格数量 | `URigLogicModule` |
| `Get LOD Count` | 获取可用 LOD 级别数 | `URigLogicModule` |
| `Set LOD` | 设置当前活动的 LOD 级别 | `URigLogicModule` |

### 使用示例

1. **基本驱动流程**：通过 AnimBlueprint 的 AnimNode_RigLogic 节点，将 ControlRig 输出的控制属性映射到面部网格变形
2. **动态 LOD**：根据角色与摄像机距离，通过 `Set LOD` 节点切换面部动画的精度级别
3. **控制属性监控**：使用 `Get Control Attribute Values` 节点配合 Print String 调试面部动画状态

## C++ 用法

### 头文件引入

```cpp
#include "RigLogicModule.h"
#include "DNAAsset.h"
```

### 基本用法

```cpp
// 加载 DNA 资产并设置到骨骼网格
UDNAAsset* DNAAsset = LoadObject<UDNAAsset>(nullptr, TEXT("/Game/Characters/MyMetaHuman/face_DNA"));
if (DNAAsset)
{
    // 设置到 SkeletalMeshComponent 的 AnimInstance
    AnimInstance->SetDNAAsset(DNAAsset);
}
```

### 进阶用法

```cpp
// 直接访问 RigLogic 库进行自定义计算
FRigLogicInstance RigInstance;
RigInstance.SetDNAReader(DNAReader);
RigInstance.Calculate();

// 获取控制属性并手动更新
TArray<float> ControlValues = RigInstance.GetControlAttributeValues();
// 修改 ControlValues...
RigInstance.SetControlAttributeValues(ControlValues);
RigInstance.Calculate();
```

## Demo 示例

```cpp
// RigLogicDemoActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RigLogicDemoActor.generated.h"

class USkeletalMeshComponent;
class UDNAAsset;

UCLASS()
class ARigLogicDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ARigLogicDemoActor();

    UPROPERTY(VisibleAnywhere)
    USkeletalMeshComponent* FaceMesh;

    UPROPERTY(EditAnywhere, Category = "RigLogic")
    UDNAAsset* DNAAsset;

    UPROPERTY(EditAnywhere, Category = "RigLogic")
    float JawOpen = 0.0f;

    UPROPERTY(EditAnywhere, Category = "RigLogic")
    float Smile = 0.0f;

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;
};

// RigLogicDemoActor.cpp
#include "RigLogicDemoActor.h"
#include "Components/SkeletalMeshComponent.h"
#include "DNAAsset.h"

ARigLogicDemoActor::ARigLogicDemoActor()
{
    FaceMesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("FaceMesh"));
    RootComponent = FaceMesh;
    PrimaryActorTick.bCanEverTick = true;
}

void ARigLogicDemoActor::BeginPlay()
{
    Super::BeginPlay();
    if (DNAAsset && FaceMesh)
    {
        // DNA 资产通过 AnimBP 自动应用到面部网格
    }
}

void ARigLogicDemoActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    // 控制属性通过 AnimBP 中的 AnimNode_RigLogic 驱动
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MessageLog` | DNA 文件导入错误日志 |
| `SkeletalMeshUtilitiesCommon` | 骧骼网格工具函数 |
| `RHI` / `RenderCore` | GPU 计算支持（可选） |
| `AssetRegistry` | DNA 资产注册和发现 |
| `RigLogicLib` | 核心 ML 运行时（RigLogicModule 依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `de0806c7` | Fix RigLogic NaN output from TwistSwing/RBF when ControlAttributeCurves overwrites driver-joint quat | 修复控制属性曲线覆盖驱动关节四元数时的 NaN 输出 |
| 2026-05-13 | `52da7ee0` | Fix quaternion joints evaluator test in case no rotation support is compiled in for the zyx sequence | 修复 ZYX 旋转序列未编译时的四元数关节测试 |
| 2026-05-13 | `27f94d1b` | Fix RigLogic ML Joints initialization of rotation adapter in the absence of coordinate system conversion | 修复缺少坐标系转换时 ML 关节旋转适配器初始化 |
| 2026-05-13 | `4b5d4e7d` | Notify dependent AnimNode_RigLogic instances when RigRuntimeContext is reinitialized due to config change | 配置变更重初始化时通知依赖的 AnimNode 实例 |
| 2026-05-12 | `9006d42c` | Implement identical integration tests for all three RigLogic runtime integrations | 实现所有三种 RigLogic 运行时集成的统一集成测试 |

### 维护评价

**活跃维护** ✅

- **创建时间**：2020 年 7 月，约 5 年历史
- **最近更新**：2026 年 5 月有密集的功能性修复和测试完善
- **维护频率**：活跃，持续修复 NaN 输出、旋转计算、坐标系转换等核心问题
- **已知限制**：
  - 仅支持 MetaHuman 或自定义 DNA 格式的角色
  - `Installed: false`，需手动在插件设置中启用
  - DNA 资产需从 DCC 工具单独导出
- **推荐程度**：⭐⭐⭐⭐⭐ 强烈推荐用于 MetaHuman 或需要高保真面部动画的项目

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/RigLogic)
- [DNA 文件格式文档](https://docs.unrealengine.com/5.8/en-US/working-with-dna-in-unreal-engine/)
- [MetaHuman 官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/RigLogic/Source/RigLogicLibTest)