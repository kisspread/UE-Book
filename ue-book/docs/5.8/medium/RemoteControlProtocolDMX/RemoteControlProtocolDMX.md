# Remote Control Protocol DMX

> Allows interactions between DMX and RemoteControl API.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | DMX 远程控制协议 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、预设模板） |
| 模块 | `RemoteControlProtocolDMX` (Runtime), `RemoteControlProtocolDMXEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2021-04-08 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControlProtocolDMX) | |

## 用途

本插件是 UE5 **远程控制 API** 与 **DMX 协议** 之间的桥梁，解决了以下核心问题：

1. **DMX 信号控制引擎属性**：允许来自灯光控制台（GrandMA、ETC 等）的 DMX 信号实时控制 UE5 中任意暴露的属性（Transform、材质参数、光源强度等）
2. **自动化 Fixture Patch 管理**：自动将远程控制预设中的属性映射到 DMX Library 的 Fixture Patch，无需手动配置每个通道
3. **虚拟制片灯光同步**：在虚拟制片场景中，实现物理灯光设备与引擎内虚拟灯光/材质的实时同步

核心工作流程：`DMX 控制台 → DMX 信号 → Fixture Patch → RemoteControl API → 引擎属性`

## 使用场景

- **虚拟制片 LED 墙**：使用灯光控制台控制 UE5 中的光源强度、色温、方向等参数
- **实时演出控制**：演唱会/活动中，通过 DMX 信号实时调整引擎中的粒子效果、材质参数
- **建筑可视化**：用 DMX 调光器控制虚拟场景中的灯光氛围
- **XR 拍摄**：在 LED Volume 拍摄中，同步物理灯具与引擎灯光参数
- **主题公园/展览**：通过 DMX 控制引擎中的互动内容响应

## 蓝图用法

本插件主要通过 Remote Control 窗口和 DMX Library 配置界面操作，核心逻辑通过 UObject 属性配置驱动。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetOrCreateDMXUserData` | 获取或创建预设的 DMX 用户数据 | `URemoteControlDMXUserData` |
| `SetDMXLibrary` | 设置关联的 DMX Library 资产 | `URemoteControlDMXUserData` |
| `SetPatchGroupMode` | 设置分组模式（按属性/按对象） | `URemoteControlDMXUserData` |
| `SetAutoPatchEnabled` | 启用/禁用自动补丁分配 | `URemoteControlDMXUserData` |
| `SetAutoAssignFromUniverse` | 设置自动分配起始宇宙 | `URemoteControlDMXUserData` |
| `GetDMXLibrary` | 获取当前 DMX Library | `URemoteControlDMXUserData` |
| `GetDMXLibraryProxy` | 获取 DMX Library 代理对象 | `URemoteControlDMXUserData` |
| `Refresh` | 刷新 DMX 库代理 | `URemoteControlDMXLibraryProxy` |
| `Reset` | 重置代理，停止接收 DMX | `URemoteControlDMXLibraryProxy` |

### 使用示例（蓝图描述）

**基础配置流程：**

1. 在 Remote Control 窗口中暴露需要控制的属性（如灯光强度、颜色）
2. 在 Remote Control 预设的细节面板中找到 "DMX User Data" 设置
3. 指定一个 DMX Library 资产
4. 启用 Auto Patch 模式（默认启用），系统自动分配 DMX 通道
5. 或禁用 Auto Patch，手动在 Fixture Patch 中配置通道映射

**分组模式选择：**

- `GroupByProperty`：每个属性独立分配一个 Fixture Patch（细粒度控制）
- `GroupByOwner`：同一对象的所有属性共享一个 Fixture Patch（推荐，通道更紧凑）

**DMX 实体额外设置：**

- `bIsPrimaryPatch`：是否为主补丁（定义 Fixture Type 和 Patch 配置）
- `FunctionIndex`：DMX 功能索引
- `AttributeName`：DMX 属性名称（如 Intensity、Color、Pan 等）
- `bUseLSB`：最低有效字节模式（影响多字节数值的解析顺序）
- `DataType`：数据格式（8Bit/16Bit/24Bit）

## C++ 用法

### 头文件引入

```cpp
#include "RemoteControlProtocolDMX.h"
#include "RemoteControlDMXUserData.h"
#include "RemoteControlDMXLibraryProxy.h"
```

### 基本用法

获取 Remote Control 预设的 DMX 配置：

```cpp
// 来源: RemoteControlDMXUserData.h
// 获取或创建预设的 DMX 用户数据
URemoteControlDMXUserData* DMXUserData = URemoteControlDMXUserData::GetOrCreateDMXUserData(MyPreset);

// 设置 DMX Library
UDMXLibrary* MyLibrary = LoadObject<UDMXLibrary>(nullptr, TEXT("/Game/DMX/MyDMXLibrary"));
DMXUserData->SetDMXLibrary(MyLibrary);

// 启用自动补丁分配
DMXUserData->SetAutoPatchEnabled(true);
DMXUserData->SetAutoAssignFromUniverse(1);
```

### 高级用法

**获取所有 DMX 协议实体：**

```cpp
// 来源: RemoteControlProtocolDMX.h - FRemoteControlDMXProtocolEntity
// 获取预设中所有 DMX 协议实体
TArray<TSharedRef<TStructOnScope<FRemoteControlProtocolEntity>>> AllEntities = 
    FRemoteControlDMXProtocolEntity::GetAllDMXProtocolEntitiesInPreset(MyPreset);

// 查找特定属性关联的 DMX 实体
TArray<TSharedRef<TStructOnScope<FRemoteControlProtocolEntity>>> PropertyEntities = 
    FRemoteControlDMXProtocolEntity::FindEntitiesByProperty(MyProperty);
```

**绑定/解绑 DMX 协议：**

```cpp
// 来源: RemoteControlProtocolDMX.h - FRemoteControlProtocolDMX
// 获取 DMX 协议实例
FRemoteControlProtocolDMX* DMXProtocol = static_cast<FRemoteControlProtocolDMX*>(
    FRemoteControlProtocolManager::Get().FindProtocol(FRemoteControlProtocolDMX::ProtocolName));

// 绑定新的协议实体
TSharedRef<TStructOnScope<FRemoteControlProtocolEntity>> Entity = MakeShared<TStructOnScope<FRemoteControlProtocolEntity>>();
Entity->InitializeAs<FRemoteControlDMXProtocolEntity>();
DMXProtocol->Bind(Entity);

// 查看所有绑定
TConstArrayView<FRemoteControlProtocolEntityWeakPtr> Bindings = DMXProtocol->GetProtocolBindings();
```

**DMX Library 代理操作：**

```cpp
// 来源: RemoteControlDMXLibraryProxy.h
// 获取 DMX Library 代理
URemoteControlDMXLibraryProxy* LibraryProxy = DMXUserData->GetDMXLibraryProxy();

// 获取 DMX Library
UDMXLibrary* Library = LibraryProxy->GetDMXLibrary();

// 获取属性补丁
TArray<TSharedRef<FRemoteControlDMXControlledPropertyPatch>> Patches = LibraryProxy->GetPropertyPatches();

// 请求刷新（在帧末尾执行）
LibraryProxy->RequestRefresh();

// 立即刷新
LibraryProxy->Refresh();
```

**监听属性补丁变化（编辑器）：**

```cpp
// 来源: RemoteControlDMXLibraryProxy.h
#if WITH_EDITOR
// 监听补丁变化前
URemoteControlDMXLibraryProxy::GetOnPrePropertyPatchesChanged().AddLambda([](/*...*/){
    // 补丁即将变化
});

// 监听补丁变化后
URemoteControlDMXLibraryProxy::GetOnPostPropertyPatchesChanged().AddLambda([](){
    // 补丁已变化
});
#endif
```

## Demo 示例

完整的 DMX 远程控制绑定示例：

```cpp
// RemoteControlDMXExample.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RemoteControlDMXExample.generated.h"

class URemoteControlPreset;
class URemoteControlDMXUserData;
class UDMXLibrary;

UCLASS()
class ARemoteControlDMXExample : public AActor
{
    GENERATED_BODY()

public:
    ARemoteControlDMXExample();

    UPROPERTY(EditAnywhere, Category = "DMX Setup")
    TObjectPtr<URemoteControlPreset> RemoteControlPreset;

    UPROPERTY(EditAnywhere, Category = "DMX Setup")
    TObjectPtr<UDMXLibrary> DMXLibrary;

    UPROPERTY(EditAnywhere, Category = "DMX Setup")
    bool bUseAutoPatch = true;

    UPROPERTY(EditAnywhere, Category = "DMX Setup", meta = (EditCondition = "bUseAutoPatch"))
    int32 AutoAssignFromUniverse = 1;

    UFUNCTION(BlueprintCallable, Category = "DMX Setup")
    void InitializeDMXBinding();

    UFUNCTION(BlueprintCallable, Category = "DMX Setup")
    void RefreshDMX();

    UFUNCTION(BlueprintCallable, Category = "DMX Setup")
    void ShutdownDMX();
};
```

```cpp
// RemoteControlDMXExample.cpp
#include "RemoteControlDMXExample.h"
#include "RemoteControlProtocolDMX.h"
#include "RemoteControlDMXUserData.h"
#include "RemoteControlDMXLibraryProxy.h"
#include "RemoteControlPreset.h"
#include "DMXLibrary.h"

ARemoteControlDMXExample::ARemoteControlDMXExample()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ARemoteControlDMXExample::InitializeDMXBinding()
{
    if (!RemoteControlPreset || !DMXLibrary)
    {
        UE_LOG(LogTemp, Warning, TEXT("RemoteControlDMXExample: Preset and DMX Library must be set"));
        return;
    }

    // 获取或创建 DMX 用户数据
    URemoteControlDMXUserData* DMXUserData = URemoteControlDMXUserData::GetOrCreateDMXUserData(RemoteControlPreset);
    if (!DMXUserData)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to get DMX User Data"));
        return;
    }

    // 设置 DMX Library
    DMXUserData->SetDMXLibrary(DMXLibrary);

    // 配置自动补丁
    DMXUserData->SetAutoPatchEnabled(bUseAutoPatch);
    if (bUseAutoPatch)
    {
        DMXUserData->SetAutoAssignFromUniverse(AutoAssignFromUniverse);
    }

    // 刷新 DMX Library 代理
    URemoteControlDMXLibraryProxy* Proxy = DMXUserData->GetDMXLibraryProxy();
    if (Proxy)
    {
        Proxy->Refresh();
    }

    UE_LOG(LogTemp, Log, TEXT("DMX binding initialized successfully"));
}

void ARemoteControlDMXExample::RefreshDMX()
{
    if (!RemoteControlPreset) return;

    URemoteControlDMXUserData* DMXUserData = URemoteControlDMXUserData::GetOrCreateDMXUserData(RemoteControlPreset);
    if (DMXUserData)
    {
        URemoteControlDMXLibraryProxy* Proxy = DMXUserData->GetDMXLibraryProxy();
        if (Proxy)
        {
            Proxy->RequestRefresh();
        }
    }
}

void ARemoteControlDMXExample::ShutdownDMX()
{
    if (!RemoteControlPreset) return;

    URemoteControlDMXUserData* DMXUserData = URemoteControlDMXUserData::GetOrCreateDMXUserData(RemoteControlPreset);
    if (DMXUserData)
    {
        URemoteControlDMXLibraryProxy* Proxy = DMXUserData->GetDMXLibraryProxy();
        if (Proxy)
        {
            Proxy->Reset();
        }
    }

    UE_LOG(LogTemp, Log, TEXT("DMX binding shut down"));
}
```

## 模块依赖

从 Build.cs 的依赖关系提取（排除常见依赖）：

| 模块 | 用途 |
|---|---|
| `RemoteControl` | 核心远程控制 API，提供属性暴露和控制机制 |
| `DMXProtocol` | DMX 协议底层实现，处理 DMX 信号收发 |
| `DMXEngine` | DMX 引擎，提供 Fixture Library、Fixture Patch 等核心 DMX 对象 |
| `DMXRuntime` | DMX 运行时，处理 DMX 数据映射和信号处理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF，适配引擎日志系统重构 |
| 2025-09-16 | `77ee7eae` | Motion Design: removed beta tag from motion design plugins. | Motion Design 相关插件移除 Beta 标签 |
| 2025-04-09 | `5b3f195a` | Remote Control: Fixed issue with re-applying signatures clearing the DMX Library | 修复重新应用签名时清空 DMX Library 的问题 |
| 2025-04-03 | `9fc06e81` | Remote Control: Add struct referenced objects to protocol bindings to consider protocol entity | 协议绑定中添加结构体引用对象以正确处理协议实体 |
| 2025-04-03 | `e232a05a` | Remote Control: fixed issue where the protocols kept running even after the RC asset window was clos | 修复 RC 资产窗口关闭后协议仍在运行的问题 |

### 维护评价

**✅ 活跃维护**

- **创建时间**：2021 年 4 月，约 4 年历史
- **最近更新**：2026 年 4 月仍有实质性更新（日志系统适配）
- **更新频率**：2025 年有多次重要 bug 修复和功能改进
- **维护团队**：Epic Games 官方维护，作为虚拟制片核心功能的一部分
- **API 稳定性**：有完整的废弃标记机制，向前兼容处理良好（如 5.5 版本的输入端口废弃）
- **已知限制**：默认未启用，需手动在插件设置中启用；依赖 DMX 相关插件生态

**推荐使用**：适合虚拟制片场景中需要 DMX 灯光控制的项目。建议配合 RemoteControl 和 DMXEngine 插件一起使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControlProtocolDMX)
- [Remote Control 文档](https://docs.unrealengine.com/en-US/remote-control-in-unreal-engine/)
- [DMX 插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX)