# Android Runtime Permission

> Support for Android Runtime Permission

| 属性 | 值 |
|---|---|
| 中文名 | 安卓权限 |
| 分类 | Android |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidPermission` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-02-06 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidPermission) | |

## 用途

该插件提供了在 Android 6.0 (API Level 23) 及以上版本中动态请求和管理运行时权限的完整功能。它封装了原生 Android 权限 API，为 Unreal Engine 开发者（特别是蓝图用户）提供了易于使用的接口，以检查当前应用是否已获得特定权限（如相机、存储、定位等），并在需要时向用户发起权限请求。它解决了旧版 Android 无需动态申请权限，但新版本必须处理权限申请生命周期的兼容性问题。

## 使用场景

- 你的游戏或应用需要访问设备的敏感功能，例如相机、麦克风、内部/外部存储、精确位置或通讯录。
- 你在开发一个需要保存游戏进度或截图到用户相册的应用，这需要请求存储权限。
- 你在实现一个基于地理位置的游戏功能，需要请求位置权限。
- 你需要确保应用符合 Android 最新版本的权限管理规范。

## 蓝图用法

该插件的核心功能通过蓝图函数库 (`UAndroidPermissionFunctionLibrary`) 暴露，主要提供两个节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Check Android Permission` | 检查某个特定的 Android 权限是否已被授予。返回布尔值。 | `UAndroidPermissionFunctionLibrary` |
| `Request Android Permissions` | 向用户请求一个或多个权限。返回一个 `UAndroidPermissionCallbackProxy` 对象，其委托 `OnPermissionsGrantedDynamicDelegate` 会在权限请求结果返回时触发。 | `UAndroidPermissionFunctionLibrary` |

### 使用示例（蓝图描述）

1.  **检查权限**：
    - 拖拽 `Check Android Permission` 节点到蓝图。
    - 在 `permission` 参数中输入要检查的权限字符串（例如 `"android.permission.WRITE_EXTERNAL_STORAGE"`）。
    - 根据返回的布尔值决定是继续操作还是提示用户。

2.  **请求权限并监听结果**：
    - 创建一个 `Request Android Permissions` 节点。
    - 在 `permissions` 数组中填入一个或多个权限字符串（例如 `[“android.permission.CAMERA”, “android.permission.WRITE_EXTERNAL_STORAGE”]`）。
    - 将该节点的返回值（一个 `UAndroidPermissionCallbackProxy` 对象）保存到变量中。
    - 从该变量引出 `Assign On Permissions Granted Dynamic Delegate` 节点，绑定一个自定义的自定义事件。
    - 在该自定义事件中，根据传入的 `Permissions` 和 `Grant Results` 数组（均为布尔值）来判断每个权限是否被授予，并执行相应逻辑。

## C++ 用法

C++ 用法与蓝图 API 对应，主要涉及两个类：`UAndroidPermissionFunctionLibrary` 和 `UAndroidPermissionCallbackProxy`。

### 头文件引入

```cpp
#include "AndroidPermissionFunctionLibrary.h"
#include "AndroidPermissionCallbackProxy.h"
```

### 基本用法

以下示例展示了如何在 C++ 中检查权限并请求权限。

```cpp
// 假设在某个 Actor 或 GameInstance 的方法中

// 1. 检查权限
FString Permission = TEXT("android.permission.WRITE_EXTERNAL_STORAGE");
bool bIsGranted = UAndroidPermissionFunctionLibrary::CheckPermission(Permission);

if (bIsGranted)
{
    UE_LOG(LogTemp, Log, TEXT("权限已授予: %s"), *Permission);
    // 执行需要权限的操作
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("权限未授予: %s"), *Permission);
}

// 2. 请求权限
TArray<FString> PermissionsToRequest;
PermissionsToRequest.Add(TEXT("android.permission.CAMERA"));
PermissionsToRequest.Add(TEXT("android.permission.RECORD_AUDIO"));

// 获取回调代理
UAndroidPermissionCallbackProxy* CallbackProxy = UAndroidPermissionFunctionLibrary::AcquirePermissions(PermissionsToRequest);

if (CallbackProxy)
{
    // 绑定委托
    CallbackProxy->OnPermissionsGrantedDynamicDelegate.AddDynamic(this, &AMyActor::OnPermissionsReceived);
}
```

### 进阶用法

你可以在绑定委托的回调函数中处理复杂的权限逻辑，并根据授权结果决定后续流程。

```cpp
// 回调函数实现
UFUNCTION()
void AMyActor::OnPermissionsReceived(const TArray<FString>& Permissions, const TArray<bool>& GrantResults)
{
    bool bAllGranted = true;
    for (int32 i = 0; i < Permissions.Num(); ++i)
    {
        if (GrantResults.IsValidIndex(i) && GrantResults[i])
        {
            UE_LOG(LogTemp, Log, TEXT("权限 %s 已被授予。"), *Permissions[i]);
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("权限 %s 被拒绝。"), *Permissions[i]);
            bAllGranted = false;
        }
    }

    if (bAllGranted)
    {
        // 所有请求的权限都被授予，执行最终操作（如打开相机或保存文件）
        StartCameraCapture();
    }
    else
    {
        // 处理部分或全部权限被拒绝的情况，可能显示提示或禁用相关功能
        ShowPermissionDeniedWarning();
    }
}
```

## Demo 示例

一个完整的最小示例，展示如何在 Actor 中请求相机权限并在成功后打印日志。

**MyPermissionActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AndroidPermissionCallbackProxy.h"
#include "MyPermissionActor.generated.h"

UCLASS()
class AMyPermissionActor : public AActor
{
    GENERATED_BODY()
public:
    AMyPermissionActor();
protected:
    virtual void BeginPlay() override;

    UFUNCTION()
    void OnCameraPermissionReceived(const TArray<FString>& Permissions, const TArray<bool>& GrantResults);

private:
    UPROPERTY()
    UAndroidPermissionCallbackProxy* PermissionProxy;
};
```

**MyPermissionActor.cpp**
```cpp
#include "MyPermissionActor.h"
#include "AndroidPermissionFunctionLibrary.h"

AMyPermissionActor::AMyPermissionActor()
{
    PrimaryActorTick.bCanEverTick = false;
    PermissionProxy = nullptr;
}

void AMyPermissionActor::BeginPlay()
{
    Super::BeginPlay();

    // 检查是否已授权
    if (UAndroidPermissionFunctionLibrary::CheckPermission(TEXT("android.permission.CAMERA")))
    {
        UE_LOG(LogTemp, Log, TEXT("相机权限已存在，直接使用。"));
    }
    else
    {
        // 请求权限
        TArray<FString> Permissions;
        Permissions.Add(TEXT("android.permission.CAMERA"));

        PermissionProxy = UAndroidPermissionFunctionLibrary::AcquirePermissions(Permissions);
        if (PermissionProxy)
        {
            PermissionProxy->OnPermissionsGrantedDynamicDelegate.AddDynamic(this, &AMyPermissionActor::OnCameraPermissionReceived);
            UE_LOG(LogTemp, Log, TEXT("正在请求相机权限..."));
        }
    }
}

void AMyPermissionActor::OnCameraPermissionReceived(const TArray<FString>& Permissions, const TArray<bool>& GrantResults)
{
    // 清理委托绑定
    if (PermissionProxy)
    {
        PermissionProxy->OnPermissionsGrantedDynamicDelegate.RemoveDynamic(this, &AMyPermissionActor::OnCameraPermissionReceived);
        PermissionProxy = nullptr;
    }

    if (GrantResults.Num() > 0 && GrantResults[0])
    {
        UE_LOG(LogTemp, Log, TEXT("相机权限授予成功！"));
        // 在这里初始化相机相关功能
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("相机权限被拒绝。"));
        // 处理权限被拒逻辑
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移到新的 UE_LOGF 格式。 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i | 为模块导出的符号添加正确的 DLL 导出/导入声明。 |
| 2024-11-10 | `66e9bb39` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base | 清理代码中已废弃的 include 顺序宏，适配 UE 5.2+。 |
| 2023-02-20 | `6a4206d4` | Removing bad Launch include paths from programs. | 修复了程序构建时的头文件路径问题。 |
| 2023-01-26 | `a0774c71` | Fixed non unity/pch errors reported by build farm building non pch and non unity | 修复了非统一头文件/预编译头构建时的错误。 |

### 维护评价

该插件创建于 2017 年，历史较长。从 Git 记录看，最后一次实质性的功能或维护更新发生在 2025 年 4 月（进行 DLL 符号导出规范化），此后仅有一些针对构建系统和代码清理的更新。虽然插件被标记为 `IsBetaVersion=true`，但其核心 API (`CheckPermission`, `AcquirePermissions`) 已经稳定，并在 Android 权限请求这一特定需求上提供了有效且经过长时间检验的解决方案。

插件处于**维护状态**，但非活跃开发。它能完成其设计目标，且没有已知的阻断性问题。对于需要 Android 运行时权限管理的项目，它仍然是一个可靠的选择，尤其适合通过蓝图快速集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidPermission)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/AndroidPermissionTest)（如果存在）