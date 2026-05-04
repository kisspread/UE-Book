# Android Runtime Permission

> Support for Android Runtime Permission

| 属性 | 值 |
|---|---|
| 分类 | Android |
| 默认启用 | ✅ |
| 包含内容 | ❌ |
| 模块 | AndroidPermission (Runtime) |
| 创建时间 | 2017-02-06 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AndroidPermission) | |

> ⚠️ 注意：`.uplugin` 中 `IsBetaVersion = true`，该插件一直处于 Beta 状态。

## 用途

AndroidPermission 是 UE 内置的 Android 运行时权限请求插件。Android 6.0（API 23）起，应用必须在运行时动态请求危险权限（如相机、麦克风、存储、定位等），而非仅在 `AndroidManifest.xml` 中声明。这个插件封装了 JNI 调用，让蓝图和 C++ 代码可以方便地检查和请求 Android 运行时权限。

插件通过一个 Java 类 `com.google.vr.sdk.samples.permission.PermissionHelper`（最初来自 Google VR SDK 的示例代码）执行实际的权限检查和请求操作，然后通过 JNI 回调将结果传回 UE。

## 使用场景

- 你的游戏需要访问相机、麦克风、存储等需要运行时权限的 Android 设备功能
- 你需要在使用某个功能前先检查权限是否已授予，未授予时向用户发起请求
- 你希望通过蓝图（无需 C++）完成权限请求流程

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Check Android Permission` | 检查某项权限是否已授予，返回 `bool` | `UAndroidPermissionFunctionLibrary` |
| `Request Android Permissions` | 请求一项或多项权限，返回 `UAndroidPermissionCallbackProxy` | `UAndroidPermissionFunctionLibrary` |
| `OnPermissionsGrantedDynamicDelegate` | 权限请求完成后的委托，提供权限列表和授予结果 | `UAndroidPermissionCallbackProxy` |

### 使用示例（蓝图描述）

**检查单个权限是否已授予：**

1. 节点：`Check Android Permission`
2. `permission` 输入填入权限字符串，如 `android.permission.CAMERA`
3. 返回 `true` 表示已授予，`false` 表示未授予

**请求权限并等待结果：**

1. 节点：`Request Android Permissions`
2. `permissions` 输入一个 String 数组，如 `[android.permission.CAMERA, android.permission.RECORD_AUDIO]`
3. 返回值是 `UAndroidPermissionCallbackProxy` 对象
4. 从该对象拉出 `OnPermissionsGrantedDynamicDelegate` 委托，绑定事件
5. 事件触发时，`Permissions` 数组包含请求的权限名，`GrantResults` 数组包含对应的授予状态（`true` = 已授予）

**典型流程：**
```
[BeginPlay] → [Check Android Permission "CAMERA"]
    ├── true  → 继续使用相机
    └── false → [Request Android Permissions ["CAMERA"]]
                    └── [OnPermissionsGrantedDynamicDelegate] → 检查结果
```

## C++ 用法

### 头文件引入

```cpp
#include "AndroidPermissionFunctionLibrary.h"
#include "AndroidPermissionCallbackProxy.h"
```

### 基本用法

**检查权限（同步）：**

```cpp
// 检查相机权限是否已授予
bool bGranted = UAndroidPermissionFunctionLibrary::CheckPermission(
    TEXT("android.permission.CAMERA"));

if (bGranted)
{
    UE_LOG(LogTemp, Log, TEXT("Camera permission already granted"));
}
```

**请求权限（异步，带委托回调）：**

```cpp
// 请求多个权限
TArray<FString> Permissions;
Permissions.Add(TEXT("android.permission.CAMERA"));
Permissions.Add(TEXT("android.permission.RECORD_AUDIO"));

UAndroidPermissionCallbackProxy* Proxy = 
    UAndroidPermissionFunctionLibrary::AcquirePermissions(Permissions);

// 绑定 C++ 委托
Proxy->OnPermissionsGrantedDelegate.AddLambda(
    [](const TArray<FString>& InPermissions, const TArray<bool>& GrantResults)
    {
        for (int32 i = 0; i < InPermissions.Num(); i++)
        {
            UE_LOG(LogTemp, Log, TEXT("Permission %s: %s"),
                *InPermissions[i],
                GrantResults[i] ? TEXT("Granted") : TEXT("Denied"));
        }
    });
```

### 进阶用法

**在 C++ 中绑定蓝图委托：**

```cpp
UAndroidPermissionCallbackProxy* Proxy = 
    UAndroidPermissionFunctionLibrary::AcquirePermissions(Permissions);

Proxy->OnPermissionsGrantedDynamicDelegate.AddDynamic(
    this, &UMyClass::OnPermissionResult);
```

其中 `OnPermissionResult` 是一个 `UFUNCTION`：

```cpp
UFUNCTION()
void OnPermissionResult(const TArray<FString>& Permissions, const TArray<bool>& GrantResults);
```

## 内部实现说明

- `UAndroidPermissionCallbackProxy` 是一个全局单例（通过 `AddToRoot()` 防止 GC 回收）
- 权限请求通过 JNI 调用 Java 侧的 `PermissionHelper.acquirePermissions()`
- Java 侧回调 `onAcquirePermissions` 通过 `FFunctionGraphTask` 将结果派发到游戏线程
- 在非 Android 平台（编辑器/桌面），`CheckPermission` 始终返回 `false`，`AcquirePermissions` 会记录日志但不会实际请求
- 依赖的 Java 库位于 `Engine/Source/ThirdParty/AndroidPermission/permission_library`，打包时自动复制到 `JavaLibs/permission_library`

## 模块依赖

从 `AndroidPermission.Build.cs` 提取。你的项目模块如果要使用此插件，需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `Engine` | UE 引擎核心（UObject、蓝图系统等） |
| `CoreUObject` | UObject 系统（私有依赖） |
| `Slate` / `SlateCore` | UI 框架（私有依赖，实际未在代码中使用） |

`Build.cs` 中还通过 `AndroidPermission_APL.xml` 在 Android 打包时自动处理：
- 将 `permission_library` Java 库复制到构建目录
- 添加 ProGuard 保留规则（`com.google.vr.sdk.samples.permission.**`）
- 添加 Gradle 依赖 `com.android.support:support-v13:27.1.0`

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-04-23 | `89df8c170d23` | UnrealGame build target - dll export 转换 | UE 全局重构，非插件功能性更新 |
| 2024-11-09 | `66e9bb39ff7e` | 移除 UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 | 代码清理，非功能性更新 |
| 2023-02-20 | `6a4206d490b8` | 移除错误的 Launch include paths | 构建修复，非功能性更新 |

### 维护评价

- **创建于 2017 年**，已存在约 9 年，属于老古董级插件
- **自 2017 年创建以来无任何功能性更新**，最近 3 次提交全部是 UE 全局代码清理/重构的副作用
- 插件 API 极其简单（2 个函数 + 1 个委托），功能完整但未扩展
- `IsBetaVersion = true` 从未被移除，官方似乎将其视为实验性质
- 依赖的 Java 库来自 Google VR SDK 示例代码（`com.google.vr.sdk.samples.permission`），技术债明显
- Gradle 依赖使用旧版 `com.android.support:support-v13:27.1.0`，而非 AndroidX
- **建议**：对于简单需求可继续使用，但对于复杂场景（如自定义权限提示 UI、权限组管理）可能需要自行封装。如果对长期维护有顾虑，可考虑使用 `AndroidPermissionBPLibrary` 等社区替代方案或自行通过 JNI 实现。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AndroidPermission)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
- 测试用例：无（未找到相关自动化测试）
