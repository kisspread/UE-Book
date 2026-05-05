# VirtualCameraCore

> Code for actors, components, and utilities for controlling and viewing cameras via physical devices. See VirtualCamera for content.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `VCamCore` (Runtime), `VCamBlueprintNodes` (Runtime), `VCamCoreEditor` (Runtime), `DecoupledOutputProvider` (Runtime), `PixelStreamingVCam` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-02-07 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualCameraCore) | |

## 用途

VirtualCameraCore 是 Unreal Engine 虚拟制片（Virtual Production）工作流的核心插件，提供通过物理设备（如 iPad、手机等）远程控制和查看虚拟摄像机的完整基础设施。

该插件解决的核心问题：
- **远程摄像机控制**：允许用户通过物理设备实时操控 UE 场景中的虚拟摄像机，包括位置、旋转、焦距、光圈等参数
- **实时预览输出**：将虚拟摄像机的画面实时传输到物理设备上显示，实现所见即所得的拍摄体验
- **输出解耦架构**：通过 DecoupledOutputProvider 模块实现摄像机控制与输出显示的解耦，支持灵活的输出目标切换
- **像素流送集成**：通过 PixelStreamingVCam 模块利用 Pixel Streaming 技术实现低延迟的视频流传输
- **蓝图友好接口**：通过 VCamBlueprintNodes 提供蓝图节点，让非程序员也能配置和定制虚拟摄像机工作流

该插件是 VirtualCamera 内容插件的代码基础，VirtualCamera 提供具体的内容资产，而 VirtualCameraCore 提供底层框架和运行时逻辑。

## 使用场景

- 你在进行虚拟制片拍摄，需要导演通过 iPad 实时查看和调整虚拟摄像机角度 → 使用 VirtualCameraCore
- 你需要构建自定义的虚拟摄像机控制系统，支持多种输出目标（如 Pixel Streaming、本地预览等） → 使用 DecoupledOutputProvider 架构
- 你在开发虚拟制片工具，需要将摄像机控制逻辑与蓝图系统集成 → 使用 VCamBlueprintNodes
- 你需要通过 Pixel Streaming 将虚拟摄像机画面低延迟传输到移动设备 → 使用 PixelStreamingVCam 模块
- 你在构建多机位虚拟拍摄系统，需要灵活管理多个虚拟摄像机的输出 → 使用 VCamCore 的 Actor/Component 架构

## 模块架构

由于本插件规模较大（368 个源文件），按子模块拆分说明：

```
VirtualCameraCore/
├── VCamCore/                    ← 核心运行时模块（Actor、Component、工具类）
├── VCamBlueprintNodes/          ← 蓝图节点支持
├── VCamCoreEditor/              ← 编辑器扩展
├── DecoupledOutputProvider/     ← 解耦输出提供者架构
└── PixelStreamingVCam/          ← Pixel Streaming 集成
```

### VCamCore

核心运行时模块，包含虚拟摄像机的 Actor、Component 以及基础工具类。这是整个插件的基础，其他模块都依赖于此。

### VCamBlueprintNodes

提供蓝图友好的节点，允许用户在蓝图中配置和控制虚拟摄像机系统。无需编写 C++ 代码即可完成基本的虚拟摄像机设置。

### VCamCoreEditor

编辑器扩展模块，提供自定义的编辑器 UI、属性面板和工具栏集成，方便在编辑器中配置虚拟摄像机。

### DecoupledOutputProvider

实现输出提供者的解耦架构。将摄像机控制逻辑与具体的输出目标（如屏幕、流送、录制等）分离，使得可以灵活切换和扩展输出方式。

### PixelStreamingVCam

集成 Unreal Engine 的 Pixel Streaming 技术，实现虚拟摄像机画面通过网络低延迟传输到远程设备（如 iPad、手机浏览器等）。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Camera Component` | 设置虚拟摄像机组件的目标 | `UVCamComponent` |
| `Get Output Provider` | 获取当前的输出提供者 | `UVCamComponent` |
| `Set Output Provider` | 设置输出提供者以切换输出目标 | `UVCamComponent` |
| `Start Streaming` | 启动像素流送 | `UPixelStreamingVCamOutputProvider` |
| `Stop Streaming` | 停止像素流送 | `UPixelStreamingVCamOutputProvider` |

### 使用示例（蓝图描述）

**基本虚拟摄像机设置**：
1. 在场景中放置一个 `AVCamActor` 或向现有 Actor 添加 `UVCamComponent`
2. 通过蓝图设置摄像机的目标变换（位置、旋转）
3. 配置输出提供者（如 Pixel Streaming 或本地预览）
4. 通过物理设备连接并开始控制

**多输出目标切换**：
1. 创建多个 OutputProvider 实例（如 PixelStreaming、本地视口等）
2. 使用 `Set Output Provider` 节点在运行时切换输出目标
3. 每个输出提供者独立管理自己的渲染和传输逻辑

## C++ 用法

### 头文件引入

```cpp
#include "VCamComponent.h"
#include "VCamActor.h"
#include "OutputProvider/VCamOutputProviderBase.h"
```

### 基本用法

```cpp
// 创建虚拟摄像机组件
UVCamComponent* VCamComponent = NewObject<UVCamComponent>(OwnerActor);
VCamComponent->RegisterComponent();

// 设置摄像机目标变换
FTransform TargetTransform = FTransform(TargetRotation, TargetLocation);
VCamComponent->SetTargetTransform(TargetTransform);
```

### 进阶用法

```cpp
// 自定义输出提供者
// 继承 UVCamOutputProviderBase 实现自定义输出逻辑
UCLASS()
class UMyCustomOutputProvider : public UVCamOutputProviderBase
{
    GENERATED_BODY()
    
public:
    virtual void Activate() override;
    virtual void Deactivate() override;
    virtual void Tick(float DeltaTime) override;
};

// 在运行时切换输出提供者
VCamComponent->SetOutputProvider(MyCustomProvider);
```

## Demo 示例

```cpp
// MyVCamController.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "VCamComponent.h"
#include "MyVCamController.generated.h"

UCLASS()
class AMyVCamController : public AActor
{
    GENERATED_BODY()

public:
    AMyVCamController();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Virtual Camera")
    UVCamComponent* VCamComponent;

    UFUNCTION(BlueprintCallable, Category = "Virtual Camera")
    void UpdateCameraFromDevice(const FTransform& DeviceTransform);

protected:
    virtual void BeginPlay() override;
};
```

```cpp
// MyVCamController.cpp
#include "MyVCamController.h"

AMyVCamController::AMyVCamController()
{
    PrimaryActorTick.bCanEverTick = true;
    
    VCamComponent = CreateDefaultSubobject<UVCamComponent>(TEXT("VCamComponent"));
    RootComponent = VCamComponent;
}

void AMyVCamController::BeginPlay()
{
    Super::BeginPlay();
    
    // 初始化虚拟摄像机
    if (VCamComponent)
    {
        UE_LOG(LogTemp, Log, TEXT("Virtual Camera initialized"));
    }
}

void AMyVCamController::UpdateCameraFromDevice(const FTransform& DeviceTransform)
{
    if (VCamComponent)
    {
        VCamComponent->SetTargetTransform(DeviceTransform);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LevelEditor` | PixelStreamingVCam 模块依赖，用于编辑器集成 |
| `UnrealEd` | PixelStreamingVCam 模块依赖，用于编辑器功能 |
| `PixelStreaming` | 像素流送核心功能（PixelStreamingVCam 间接依赖） |

## 维护状态

### 近期更新

```
- dd716e4659d2 Remove ::Private from all VCamCore plugin namespaces to simplify API usage.
- 8b5ebf8064ce Move VirtualCamera and VirtualCameraCore from Plugins/Experimental Plugins/VirtualProduction
```

### 维护评价

- **创建时间**：2023-02-07，约 2 年历史
- **实验性状态**：标记为 Beta（IsBetaVersion: true），API 可能发生变化
- **最近更新**：最近的 commit 包含命名空间重构（移除 Private 命名空间以简化 API 使用），表明仍在积极优化 API 设计
- **迁移历史**：从 Experimental 目录迁移到正式的 VirtualProduction 目录，表明插件正在走向成熟
- **活跃度**：作为 Virtual Production 工作流的核心组件，预计会持续维护和更新

**综合评价**：VirtualCameraCore 是 Epic Games 官方维护的虚拟制片核心插件，虽然仍处于 Beta 状态，但已从实验性目录迁移到正式目录，表明其稳定性在不断提升。该插件是虚拟制片工作流的基础设施，推荐在虚拟制片项目中使用，但需注意 Beta 状态下 API 可能变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualCameraCore)
- [VirtualCamera 内容插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualCamera)（配套内容资产）