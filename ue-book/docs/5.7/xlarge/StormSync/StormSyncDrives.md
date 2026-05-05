# Storm Sync

> Sync, Pull, Push, asset dependencies.
>
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

StormSync 是一个用于在 Unreal Engine 项目之间或内部同步资产及其依赖关系的插件。它提供了一套完整的工具链，支持资产的拉取（Pull）、推送（Push）和同步（Sync）操作。其核心目标是简化 Motion Design 工作流中的资产管理和共享，确保团队成员或不同项目环境之间能够高效、准确地传递复杂的资产依赖关系。

## 使用场景

- 你的 Motion Design 团队需要共享和同步复杂的材质、蓝图和资产包。
- 你需要从一个中央网络位置或共享驱动器访问和更新项目资产。
- 你希望自动化资产部署流程，确保所有依赖项都被正确打包和传输。

## 蓝图用法

`StormSyncDrives` 模块主要提供配置和管理虚拟驱动器（挂载点）的功能，其核心 API 通过 C++ 接口暴露，蓝图中主要通过设置资产进行配置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MountPoints` (属性) | 配置虚拟驱动器挂载点的数组 | `UStormSyncDrivesSettings` |

### 使用示例（蓝图描述）

在蓝图中，你无法直接调用 `RegisterMountPoint` 函数。相反，你需要在项目设置中配置 `UStormSyncDrivesSettings` 资产，或者通过蓝图访问该设置对象来修改 `MountPoints` 数组。配置完成后，模块会自动处理挂载点的注册和验证。

## C++ 用法

### 头文件引入

```cpp
#include "IStormSyncDrivesModule.h"
#include "StormSyncDrivesSettings.h"
```

### 基本用法

通过模块接口注册一个新的虚拟驱动器挂载点。

```cpp
// 来源: IStormSyncDrivesModule.h
// 获取 StormSyncDrives 模块接口
IStormSyncDrivesModule& DrivesModule = IStormSyncDrivesModule::Get();

// 准备挂载点配置
FStormSyncMountPointConfig MountConfig;
MountConfig.MountPoint = TEXT("/SharedAssets");
MountConfig.MountDirectory.Path = TEXT("Z:/NetworkDrive/ProjectAssets");
MountConfig.bResolveAsRelativePath = false;

// 注册挂载点
FText ErrorText;
EStormSyncDriveErrorCode ErrorCode;
bool bSuccess = DrivesModule.RegisterMountPoint(MountConfig, ErrorText, &ErrorCode);

if (!bSuccess)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to mount drive: %s"), *ErrorText.ToString());
    // 根据 ErrorCode 处理具体错误
}
```

### 进阶用法

使用 `FStormSyncDrivesUtils` 工具类进行预验证，确保配置有效后再注册。

```cpp
// 来源: StormSyncDrivesUtils.h
FStormSyncMountPointConfig ConfigToTest;
ConfigToTest.MountPoint = TEXT("/Invalid//Path");
ConfigToTest.MountDirectory.Path = TEXT("C:/SomePath");

FText ValidationError;
EStormSyncDriveErrorCode ValidationCode;

// 先验证配置
if (FStormSyncDrivesUtils::ValidateMountPoint(ConfigToTest, ValidationError, &ValidationCode))
{
    // 验证通过，再进行注册
    IStormSyncDrivesModule::Get().RegisterMountPoint(ConfigToTest, ValidationError);
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("Validation failed: %s"), *ValidationError.ToString());
}
```

## Demo 示例

一个最小的示例，展示如何在运行时动态注册一个挂载点。

**StormSyncDrivesDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "StormSyncDrivesDemo.generated.h"

UCLASS()
class UStormSyncDrivesDemoSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

private:
    void SetupMountPoints();
};
```

**StormSyncDrivesDemo.cpp**
```cpp
#include "StormSyncDrivesDemo.h"
#include "IStormSyncDrivesModule.h"
#include "StormSyncDrivesSettings.h"

void UStormSyncDrivesDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    SetupMountPoints();
}

void UStormSyncDrivesDemoSubsystem::Deinitialize()
{
    // 可以选择在反初始化时卸载挂载点
    if (IStormSyncDrivesModule::IsAvailable())
    {
        IStormSyncDrivesModule& DrivesModule = IStormSyncDrivesModule::Get();
        FText ErrorText;
        FStormSyncMountPointConfig Config;
        Config.MountPoint = TEXT("/DemoAssets");
        DrivesModule.UnregisterMountPoint(Config, ErrorText);
    }
    Super::Deinitialize();
}

void UStormSyncDrivesDemoSubsystem::SetupMountPoints()
{
    if (!IStormSyncDrivesModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("StormSyncDrives module is not loaded."));
        return;
    }

    IStormSyncDrivesModule& DrivesModule = IStormSyncDrivesModule::Get();

    // 配置一个指向项目 Content 目录下子文件夹的挂载点
    FStormSyncMountPointConfig Config;
    Config.MountPoint = TEXT("/DemoAssets");
    // 假设有一个相对于项目内容目录的路径
    Config.MountDirectory.Path = TEXT("SharedContent/Demo");
    Config.bResolveAsRelativePath = true;

    FText ErrorText;
    if (!DrivesModule.RegisterMountPoint(Config, ErrorText))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to register demo mount point: %s"), *ErrorText.ToString());
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully registered mount point '/DemoAssets'."));
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

- a7e876813edc Refactor StormSyncDrives module to allow for command line specification of mount paths as support for relative paths.
  *解读：重构了模块，增加了对相对路径的支持，并允许通过命令行指定挂载路径，增强了灵活性。*
- d53ec51b85c0 Motion Design: moved the following plugins from /Plugins/Experimental to /Plugins/VirtualProduction: ActorModifier, ActorModifierCore, Motion Design, ClonerEffector, CustomDetailsView, Material Designer, GeometryMask, OperatorStack, PropertyAnimator, PropertyAnimatorCore, StormSync, StormSync Motion Design Bridge
  *解读：该插件已从实验性（Experimental）分类正式迁移至虚拟制作（VirtualProduction）分类，表明其已达到稳定可用的状态。*

### 维护评价

**活跃维护**。该插件创建于 2024 年初，非常年轻。近期有实质性的功能更新（支持相对路径）和重要的项目结构调整（从 Experimental 迁移至 VirtualProduction）。作为 Epic Games 官方维护的 Motion Design 工作流核心组件，预计将持续获得支持和更新。推荐在相关的虚拟制作和 Motion Design 项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncDrives)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTests)