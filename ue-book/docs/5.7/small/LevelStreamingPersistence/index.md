# Level Streaming Persistence

> Experimental Level Streaming Persistence framework

| 属性 | 值 |
|---|---|
| 分类 | Runtime |
| 默认启用 | ❌ 需手动启用 |
| 包含内容 | 否 |
| 模块 | LevelStreamingPersistence (Runtime) |
| 创建时间 | 2023-04-03 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/LevelStreamingPersistence) | |

## 用途

解决 **关卡流式加载（Level Streaming）过程中 Actor 属性丢失** 的问题。

在 World Partition 或 Level Streaming 场景下，当一个子关卡被卸载（unloaded）后重新加载时，关卡中的 Actor 会从磁盘原始数据重新实例化，这意味着运行时对 Actor 属性所做的任何修改（如位置变化、状态切换、计数器等）都会丢失。

本插件通过 `UWorldSubsystem` 自动拦截关卡的可见性切换事件，在关卡卸载前保存指定属性的当前值，并在关卡重新加载时自动恢复，从而实现属性的跨流式加载持久化。

**注意**：此插件标记为 `IsExperimentalVersion = true`，属于实验性功能。

## 使用场景

- 你在做开放世界游戏，使用 World Partition 流式加载，需要玩家在区域内做的改变（如打开的门、拾取的物品状态）在离开再回来后依然保留
- 你使用传统 Level Streaming，需要在子关卡卸载/重载之间保持某些 Actor 的运行时状态
- 你需要一个轻量级的属性持久化方案，不想自己实现完整的存档系统

## 蓝图用法

本插件 **没有暴露任何 BlueprintCallable 节点**。所有 API 均为 C++ 接口。

## C++ 用法

### 头文件引入

```cpp
#include "LevelStreamingPersistenceManager.h"
#include "LevelStreamingPersistenceModule.h"
#include "LevelStreamingPersistenceSettings.h"
```

### 启用插件

由于插件默认禁用，需要在项目的 `.uproject` 文件中手动启用：

```json
{
  "Plugins": [
    {
      "Name": "LevelStreamingPersistence",
      "Enabled": true
    }
  ]
}
```

### 配置持久化属性

在 `DefaultEngine.ini` 中配置需要持久化的属性路径：

```ini
[/Script/LevelStreamingPersistence.LevelStreamingPersistenceSettings]
+Properties=(Path="/Script/Engine.Actor:CustomProp",bIsPublic=True)
+Properties=(Path="/Script/MyGame.MyActor:Health",bIsPublic=False)
```

`Path` 格式为 `UProperty` 的完整路径（类名:属性名），`bIsPublic` 区分公有/私有属性，影响内部序列化策略。

### 基本用法：获取 Subsystem 并读写属性

`ULevelStreamingPersistenceManager` 是一个 `UWorldSubsystem`，在支持的游戏世界中自动创建（需要 World Partition 启用流式加载，且非客户端 NetMode）。

```cpp
// 获取 Manager
ULevelStreamingPersistenceManager* Manager = World->GetSubsystem<ULevelStreamingPersistenceManager>();
if (!Manager) return;

// 设置属性值（如果对象已加载则同时写入对象）
const FString ObjectPath = TEXT("/Game/Maps/MyMap.PersistentLevel.MyActor_0");
Manager->SetPropertyValue<AActor, int32>(ObjectPath, FName("Health"), 100);

// 读取属性值
int32 Health = 0;
if (Manager->GetPropertyValue<int32>(ObjectPath, FName("Health"), Health))
{
    UE_LOG(LogTemp, Log, TEXT("Health = %d"), Health);
}

// 使用字符串版本（无需知道具体类型）
Manager->TrySetPropertyValueFromString(ObjectPath, FName("Health"), TEXT("100"));

FString ValueStr;
if (Manager->GetPropertyValueAsString(ObjectPath, FName("Health"), ValueStr))
{
    UE_LOG(LogTemp, Log, TEXT("Health = %s"), *ValueStr);
}
```

### 进阶用法：自定义持久化过滤逻辑

通过 `ILevelStreamingPersistenceModule` 注册回调，可以精细控制哪些属性应该被持久化：

```cpp
ILevelStreamingPersistenceModule& Module = ILevelStreamingPersistenceManager::Get();

// 注册"是否持久化"判断回调
Module.OnShouldPersistProperty<AMyActor>().BindLambda(
    [](const UObject* Object, const FProperty* Property) -> bool
    {
        // 返回 false 表示跳过此属性
        if (Property->GetFName() == FName("bTransientFlag"))
        {
            return false;
        }
        return true;
    }
);

// 注册属性恢复后的回调
Module.OnPostRestorePersistedProperty<AMyActor>().BindLambda(
    [](const UObject* Object, const FProperty* Property)
    {
        // 恢复后执行额外逻辑，如刷新 UI、重建缓存等
    }
);
```

### 进阶用法：手动序列化与反序列化

可以将整个 Manager 的状态序列化为字节数组，用于自定义存档：

```cpp
// 保存
TArray<uint8> SaveData;
if (Manager->SerializeTo(SaveData))
{
    // 将 SaveData 写入存档文件...
}

// 加载
TArray<uint8> LoadData;
// 从存档文件读取 LoadData...
if (Manager->InitializeFrom(LoadData))
{
    // 恢复成功，已加载的关卡属性会立即恢复
}
```

### 控制台命令（非 Shipping 构建可用）

| 命令 | 说明 |
|---|---|
| `s.LevelStreamingPersistence.Enabled 0/1` | 启用/禁用持久化系统 |
| `s.LevelStreamingPersistence.Debug.DumpContent` | 打印所有已持久化的属性到日志 |
| `s.LevelStreamingPersistence.Debug.SetPropertyValue <对象路径> <属性名> <值>` | 运行时修改持久化属性值 |
| `s.LevelStreamingPersistence.Debug.GetPropertyValue <对象路径> <属性名>` | 查询持久化属性值 |
| `s.LevelStreamingPersistence.Debug.SaveToFile` | 保存到 `Saved/LevelStreamingPersistence/` 目录 |
| `s.LevelStreamingPersistence.Debug.LoadFromFile` | 从文件加载 |

## Demo 示例

### 最小可运行示例

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "LevelStreamingPersistence"
});
```

**自定义 Actor 头文件** (`MyPersistentActor.h`):

```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyPersistentActor.generated.h"

UCLASS()
class AMyPersistentActor : public AActor
{
    GENERATED_BODY()
public:
    // 此属性将在关卡流式加载时被持久化
    UPROPERTY()
    int32 InteractionCount = 0;

    // 此属性也会被持久化
    UPROPERTY()
    bool bIsActivated = false;

    UFUNCTION(BlueprintCallable)
    void Interact()
    {
        InteractionCount++;
        bIsActivated = true;
    }
};
```

**DefaultEngine.ini 配置**：

```ini
[/Script/LevelStreamingPersistence.LevelStreamingPersistenceSettings]
+Properties=(Path="/Script/MyGame.MyPersistentActor:InteractionCount",bIsPublic=True)
+Properties=(Path="/Script/MyGame.MyPersistentActor:bIsActivated",bIsPublic=True)
```

配置完成后，当包含 `AMyPersistentActor` 的子关卡被卸载再加载时，`InteractionCount` 和 `bIsActivated` 的值会自动恢复。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统、属性反射 |
| `Engine` | 关卡流式加载、World Partition |

内部私有依赖：`PropertyPath`（属性路径解析）

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2024-12-12 | `30f3b4a` | Add [[Nodiscard]] on FName and FText | 代码规范更新，非功能性改动 |
| 2024-10-28 | `4f85ca8` | Fixed linker error when building non-unity | 修复非 unity 构建的链接错误 |
| 2024-06-19 | `e6d36d7` | Remove references to deprecated plugin StructUtils | 适配引擎重构，StructUtils 合并到 CoreUObject |

### 维护评价

- **年龄**：约 3 年（2023-04 创建），仍在 🆕 范围内
- **更新频率**：最近一次实质更新在 2024-10，间隔约 4 个月
- **状态**：标记为 `IsExperimentalVersion = true`，`EnabledByDefault = false`，仍处于实验阶段
- **已知限制**：
  - 仅支持游戏世界（`EWorldType::Game` 和 `PIE`），不支持编辑器世界
  - 仅支持服务端（`NM_Client` 会被跳过）
  - 需要 World Partition 启用流式加载
  - 没有 Blueprint 接口，纯 C++ 使用
- **推荐**：适合需要关卡流式加载属性持久化的 C++ 项目，但因实验性质，生产环境使用需充分测试

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/LevelStreamingPersistence)
- 官方文档（无）
