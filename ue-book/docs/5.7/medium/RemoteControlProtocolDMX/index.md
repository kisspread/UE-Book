# Remote Control Protocol DMX

> Allows interactions between DMX and RemoteControl API.

| 属性 | 值 |
|---|---|
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（图标资源） |
| 模块 | `RemoteControlProtocolDMX` (Runtime), `RemoteControlProtocolDMXEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2021-03-18 |
| 年龄标签 | 🏛️ 文物（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControlProtocolDMX) | |

## 用途

Remote Control Protocol DMX 是 UE5 Remote Control 系统的 DMX 协议扩展插件。它将 DMX（数字多路复用）灯光控制协议与 Remote Control API 连接起来，使得 Unreal Engine 中暴露的属性可以通过 DMX 信号实时控制。

**核心解决的问题**：在虚拟制片（Virtual Production）场景中，现场灯光控制台通过 DMX 协议发送灯光参数。这个插件让你能够将这些 DMX 信号映射到 UE 中任意暴露的属性上（比如灯光强度、颜色、Actor 位置等），实现物理灯光控制台与虚拟场景的实时联动。

**工作原理**：
1. 在 Remote Control Preset 中暴露你想要控制的属性
2. 插件自动为这些属性创建 DMX Fixture Patch（或手动分配）
3. 当 DMX 数据到达时，插件通过 `OnFixturePatchReceivedDMX` 回调接收数据
4. 接收到的 DMX 属性值被映射到对应的暴露属性上

**重要说明**：此插件默认不启用（`EnabledByDefault: false`），需要在项目设置中手动启用。它依赖于 RemoteControl、DMXProtocol 和 DMXEngine 三个插件。

## 使用场景

- 你正在搭建虚拟制片环境，需要通过灯光控制台（如 grandMA、ETC）实时控制 UE 中的灯光参数 → 启用此插件
- 你需要将物理 DMX 控制台的推子/旋钮映射到 UE 中任意 Actor 的属性上 → 使用 Remote Control Preset + DMX Protocol
- 你在做一个需要 DMX 输入的交互装置艺术项目 → 通过此插件将 DMX 信号绑定到材质参数或 Actor 变换
- 你已经有 DMX Library 和 Fixture Patch，想让它们自动驱动 Remote Control 暴露的属性 → 此插件就是为此而生
- 你需要自动分配 DMX 地址，避免手动管理 Universe/Channel → 使用 Auto Patch 模式

## 蓝图用法

此插件的蓝图接口较少，主要通过 Remote Control Preset 的编辑器 UI 进行配置。核心逻辑在 C++ 层实现，运行时通过 DMX 信号驱动属性变更。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetOrCreateDMXUserData` | 获取或创建 Preset 的 DMX 用户数据 | `URemoteControlDMXUserData` |
| `GetDMXLibrary` | 获取关联的 DMX Library | `URemoteControlDMXUserData` |
| `SetDMXLibrary` | 设置 DMX Library | `URemoteControlDMXUserData` |
| `IsAutoPatch` | 查询是否启用自动 Patch 模式 | `URemoteControlDMXUserData` |
| `SetAutoPatchEnabled` | 启用/禁用自动 Patch | `URemoteControlDMXUserData` |
| `GetAllDMXProtocolEntitiesInPreset` | 获取 Preset 中所有 DMX 协议实体 | `FRemoteControlDMXProtocolEntity` |
| `FindEntitiesByProperty` | 按属性查找 DMX 协议实体 | `FRemoteControlDMXProtocolEntity` |

### 使用示例（蓝图描述）

由于此插件主要通过编辑器面板操作，典型的使用流程如下：

1. **创建 Remote Control Preset**：在 Content Browser 中右键 → Miscellaneous → Remote Control Preset
2. **暴露属性**：选中 Actor，在 Details 面板中右键属性 → Remote Control → Expose
3. **切换到 DMX 协议**：在 Remote Control 面板顶部的协议选择器中选择 "DMX"
4. **配置 DMX 设置**：在面板顶部出现的 DMX 设置区域中，可以选择 DMX Library、启用 Auto Patch 等
5. **分配 Fixture Patch**：每个暴露的属性会出现在列表中，在 Patch 列可以指定 Fixture Patch（Auto Patch 模式下自动分配）

## C++ 用法

### 头文件引入

```cpp
// Runtime 模块
#include "RemoteControlProtocolDMX.h"
#include "RemoteControlDMXUserData.h"
#include "Library/RemoteControlDMXLibraryProxy.h"

// 需要的依赖头文件
#include "RemoteControlPreset.h"
#include "RemoteControlProtocol.h"
```

### 基本用法

获取 Remote Control Preset 的 DMX 用户数据，并配置 DMX Library：

```cpp
// 来源: Source/RemoteControlProtocolDMX/Internal/RemoteControlDMXUserData.h
// 获取或创建 Preset 的 DMX 用户数据
URemoteControlDMXUserData* DMXUserData = URemoteControlDMXUserData::GetOrCreateDMXUserData(MyPreset);

// 获取当前 DMX Library
UDMXLibrary* DMXLibrary = DMXUserData->GetDMXLibrary();

// 设置新的 DMX Library
DMXUserData->SetDMXLibrary(NewDMXLibrary);

// 启用/禁用自动 Patch
DMXUserData->SetAutoPatchEnabled(true);

// 设置自动分配的起始 Universe
DMXUserData->SetAutoAssignFromUniverse(1);
```

### 进阶用法

获取 DMX 协议实例并查询绑定：

```cpp
// 来源: Source/RemoteControlProtocolDMX/Public/RemoteControlProtocolDMX.h
// 获取 DMX 协议
const TSharedPtr<IRemoteControlProtocol> DMXProtocol = 
    IRemoteControlProtocolModule::Get().GetProtocolByName(FRemoteControlProtocolDMX::ProtocolName);

TSharedPtr<FRemoteControlProtocolDMX> DMXProtocolImpl = 
    StaticCastSharedPtr<FRemoteControlProtocolDMX>(DMXProtocol);

// 查询所有绑定
TConstArrayView<FRemoteControlProtocolEntityWeakPtr> Bindings = DMXProtocolImpl->GetProtocolBindings();

// 查找 Preset 中的所有 DMX 实体
TArray<TSharedRef<TStructOnScope<FRemoteControlProtocolEntity>>> AllEntities = 
    FRemoteControlDMXProtocolEntity::GetAllDMXProtocolEntitiesInPreset(MyPreset);

// 查找特定属性的 DMX 实体
TArray<TSharedRef<TStructOnScope<FRemoteControlProtocolEntity>>> Entities = 
    FRemoteControlDMXProtocolEntity::FindEntitiesByProperty(MyProperty);
```

监听 DMX 属性变更（编辑器中）：

```cpp
// 来源: Source/RemoteControlProtocolDMX/Internal/Library/RemoteControlDMXLibraryProxy.h
// 监听属性 Patch 变更前
URemoteControlDMXLibraryProxy::GetOnPrePropertyPatchesChanged().AddLambda(
    [](URemoteControlPreset* ChangedPreset)
    {
        // 在属性 Patch 变更前处理
    });

// 监听属性 Patch 变更后
URemoteControlDMXLibraryProxy::GetOnPostPropertyPatchesChanged().AddLambda(
    []()
    {
        // 在属性 Patch 变更后处理
    });
```

### DMX 协议实体配置

```cpp
// 来源: Source/RemoteControlProtocolDMX/Public/RemoteControlProtocolDMX.h
// FRemoteControlDMXProtocolEntity 的 ExtraSetting 包含：
FRemoteControlDMXProtocolEntityExtraSetting Setting;
Setting.FixturePatchReference = MyFixturePatchRef;  // Fixture Patch 引用
Setting.AttributeName = FName("Intensity");          // DMX 属性名
Setting.DataType = EDMXFixtureSignalFormat::E16Bit;  // 数据格式（8/16/24/32 bit）
Setting.bUseLSB = true;                               // LSB 模式
Setting.bIsPrimaryPatch = true;                       // 是否为主 Patch
```

## Demo 示例

### 最小 DMX 驱动属性示例

以下代码展示如何在 C++ 中设置一个 Remote Control Preset，使其属性可以被 DMX 信号控制：

```cpp
// MyDMXControlledActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyDMXControlledActor.generated.h"

UCLASS()
class AMyDMXControlledActor : public AActor
{
    GENERATED_BODY()

public:
    // 这个属性将通过 Remote Control 暴露，然后通过 DMX 控制
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "DMX")
    float LightIntensity = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "DMX")
    FLinearColor LightColor = FLinearColor::White;
};
```

```cpp
// MyDMXSetup.cpp - 设置 Remote Control + DMX
#include "RemoteControlPreset.h"
#include "RemoteControlDMXUserData.h"
#include "RemoteControlProtocolDMX.h"
#include "IRemoteControlProtocolModule.h"

void SetupDMXControl(URemoteControlPreset* Preset, AMyDMXControlledActor* Actor)
{
    // 1. 暴露属性（通常在编辑器中通过右键菜单完成）
    // Preset->ExposeProperty(Actor, GET_MEMBER_NAME_CHECKED(AMyDMXControlledActor, LightIntensity));
    
    // 2. 获取或创建 DMX 用户数据
    URemoteControlDMXUserData* DMXUserData = 
        URemoteControlDMXUserData::GetOrCreateDMXUserData(Preset);
    
    // 3. 启用自动 Patch
    DMXUserData->SetAutoPatchEnabled(true);
    
    // 4. 设置起始 Universe
    DMXUserData->SetAutoAssignFromUniverse(1);
    
    // 5. 系统会自动为暴露的属性创建 Fixture Type 和 Fixture Patch
    // 6. 当 DMX 数据到达时，属性值会自动更新
}
```

**Build.cs 依赖**：

```csharp
// 你的模块 Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "RemoteControlProtocolDMX",  // 运行时模块
});

// 如果需要编辑器功能
if (Target.bBuildEditor)
{
    PrivateDependencyModuleNames.Add("RemoteControlProtocolDMXEditor");
}
```

## 模块依赖

### RemoteControlProtocolDMX (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `DMXRuntime` | DMX 运行时库（Fixture Patch、DMX Library 等） |
| `DMXProtocol` | DMX 协议基础实现（私有依赖） |
| `Engine` | 引擎核心（私有依赖） |
| `RemoteControl` | Remote Control 核心框架（私有依赖） |
| `RemoteControlProtocol` | Remote Control 协议接口（私有依赖） |

### RemoteControlProtocolDMXEditor (Editor)

| 模块 | 用途 |
|---|---|
| `DMXEditor` | DMX 编辑器工具 |
| `DMXProtocol` | DMX 协议 |
| `DMXRuntime` | DMX 运行时 |
| `DMXProtocolEditor` | DMX 协议编辑器 |
| `PropertyEditor` | 属性编辑器（Details 面板定制） |
| `RemoteControl` | Remote Control 核心 |
| `RemoteControlProtocol` | 协议接口 |
| `RemoteControlUI` | Remote Control UI 框架 |
| `RemoteControlProtocolWidgets` | 协议绑定列表 UI |
| `Slate` / `SlateCore` | Slate UI 框架 |
| `ToolMenus` | 工具菜单系统 |
| `UnrealEd` | 编辑器核心 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-23 | `df329aa` | Motion Design: removed beta tag from motion design plugins | Motion Design 相关插件的 beta 标签移除，可能涉及此插件的配置调整 |
| 2025-04-09 | `5b3f195` | Remote Control: Fixed issue with re-applying signatures clearing the DMX Library | 修复了重新应用签名时 DMX Library 被清空的 bug，这对 DMX 集成稳定性很重要 |
| 2025-04-03 | `9fc06e8` | Remote Control: Add struct referenced objects to protocol bindings to consider protocol entity | 改进了协议绑定中对结构体引用对象的处理，确保 DMX 实体被正确考虑 |
| 2025-04-03 | `e232a05` | Remote Control: fixed issue where the protocols kept running even after the RC asset window was closed | 修复了 RC 资产窗口关闭后协议仍继续运行的问题 |

### 维护评价

**综合评价：活跃维护中**

- **年龄**：创建于 2021 年 3 月，约 5 年历史，属于 Virtual Production 套件的一部分
- **更新频率**：2025 年有多次实质性更新，说明仍在积极维护
- **维护质量**：最近的更新集中在 bug 修复和架构改进，表明代码质量在持续提升
- **稳定性**：从 5.0 到 5.5 经历了多次重大重构（属性迁移到 ExtraSetting 结构体、引入 DMX Library 内部管理等），当前版本已趋于稳定
- **已知限制**：
  - 默认不启用，需要手动开启
  - 依赖三个其他插件（RemoteControl、DMXProtocol、DMXEngine）
  - `URemoteControlProtocolDMXSettings` 已完全废弃（5.5），设置现在通过 `URemoteControlDMXUserData` 管理
- **推荐使用**：✅ 推荐。对于需要 DMX 集成的虚拟制片项目，这是官方推荐的解决方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControlProtocolDMX)
- 无官方文档（.uplugin 中 DocsURL 为空）
- 无独立测试用例

## 内部架构

### 核心类关系

```
URemoteControlPreset
  └── URemoteControlDMXUserData (UserData)
        ├── UDMXLibrary (内部 DMX Library)
        └── URemoteControlDMXLibraryProxy (Transient)
              └── TArray<FRemoteControlDMXControlledPropertyPatch>
                    └── TArray<FRemoteControlDMXControlledProperty>
                          └── TArray<FRemoteControlDMXProtocolEntity>
```

### Patch 分组模式

`ERemoteControlDMXPatchGroupMode` 定义了两种分组策略：

| 模式 | 说明 |
|---|---|
| `GroupByProperty` | 每个属性创建独立的 Fixture Patch。适用于需要独立 DMX 地址控制每个属性的场景 |
| `GroupByOwner` | 按属性的 Owner Actor 分组，同一个 Actor 的所有属性共享一个 Fixture Patch。**默认模式**，更高效 |

### 信号格式

`EDMXFixtureSignalFormat` 定义了 DMX 信号的数据精度：

| 格式 | 字节数 | 最大值 |
|---|---|---|
| `E8Bit` | 1 | 255 |
| `E16Bit` | 2 | 65,535 |
| `E24Bit` | 4* | 16,777,215 |
| `E32Bit` | 4 | 4,294,967,295 |

*注意：24-bit 整数在内存中以 32-bit 存储，因为原生没有 24-bit 类型。

### 自动 Patch 流程

1. `FRemoteControlDMXLibraryBuilder` 监听 `OnPrePropertyPatchesChanged` 和 `OnPostPropertyPatchesChanged`
2. 当属性 Patch 变更时，`FRemoteControlDMXPatchBuilder` 创建/更新 Fixture Type 和 Fixture Patch
3. Auto Patch 模式下，`AutoAssignFixturePatches` 自动分配 Universe 和 Channel
4. 旧的 Fixture Patch 在不再被引用时自动清理
5. Fixture Patch 使用 `RCGenerated_PatchGroup: N` 标签进行分组管理

### 自动绑定（Auto Bind）

`FRemoteControlDMXAutoBindHandler` 在编辑器中持续监听 DMX 信号变化：
- 仅在 Auto Patch **禁用**时工作（与 Auto Patch 互斥）
- 比较新旧 DMX 信号，检测变化的 Channel
- 自动将变化的 Universe/Channel 绑定到当前选中的 Protocol Entity
- 这是"用控制台推子直接绑定"功能的实现
