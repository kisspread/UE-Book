# UObject Example Plugin

> An example of a plugin which declares its own UObject type. This can be used as a starting point when creating your own plugin.

| 属性 | 值 |
|---|---|
| 分类 | Developer (Examples) |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | UObjectPlugin (Runtime) |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物(>10年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/UObjectPlugin) | |

## 用途

这是 Epic Games 提供的**官方示例插件**，演示如何在 UE5 插件中声明和注册自定义的 `UObject` 派生类和 `UStruct`。它不是一个提供实际功能的插件，而是一个最小化的**模板/脚手架**，供开发者在创建自己的插件时参考。

插件展示了 UE5 插件开发的核心模式：
- 模块接口（`IModuleInterface`）的标准写法
- 在插件模块中声明 `UCLASS` 和 `USTRUCT`
- `Build.cs` 依赖配置
- `.uplugin` 文件结构

## 使用场景

- 你正在从零开始创建一个新的 UE5 插件，需要一个干净的模板作为起点
- 你想学习 UE5 插件的标准目录结构和文件组织方式
- 你需要了解如何在插件模块中正确声明 `UObject` 派生类（包含反射宏、GENERATED_UCLASS_BODY 等）

## 蓝图用法

此插件不提供任何蓝图可调用的函数或属性。它是一个纯代码示例，不暴露蓝图接口。

## C++ 用法

此插件本身不提供可复用的 API，但其源码是学习插件开发的最佳参考。

### 模块接口模式

`IUObjectPlugin.h` 展示了标准的模块接口写法：

```cpp
// 来源: Source/UObjectPlugin/Public/IUObjectPlugin.h
class IUObjectPlugin : public IModuleInterface
{
public:
    // 单例式访问
    static inline IUObjectPlugin& Get()
    {
        return FModuleManager::LoadModuleChecked<IUObjectPlugin>("UObjectPlugin");
    }

    // 检查模块是否可用
    static inline bool IsAvailable()
    {
        return FModuleManager::Get().IsModuleLoaded("UObjectPlugin");
    }
};
```

### 在插件中声明 UObject

`MyPluginObject.h` 展示了如何在插件模块中声明自定义 `USTRUCT` 和 `UCLASS`：

```cpp
// 来源: Source/UObjectPlugin/Classes/MyPluginObject.h

// 声明自定义结构体
USTRUCT()
struct FMyPluginStruct
{
    GENERATED_USTRUCT_BODY()

    UPROPERTY()
    FString TestString;
};

// 声明自定义 UObject
UCLASS()
class UMyPluginObject : public UObject
{
    GENERATED_UCLASS_BODY()

public:

private:
    UPROPERTY()
    FMyPluginStruct MyStruct;
};
```

### 模块实现

`UObjectPlugin.cpp` 展示了 `IMPLEMENT_MODULE` 宏的使用：

```cpp
// 来源: Source/UObjectPlugin/Private/UObjectPlugin.cpp
class FUObjectPlugin : public IUObjectPlugin
{
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};

IMPLEMENT_MODULE(FUObjectPlugin, UObjectPlugin)
```

### 常见问题：头文件找不到

如果你在自己的插件中引用 `MyPluginObject.h` 时遇到找不到头文件的错误，这是因为该头文件位于 `Classes/` 目录下。在 `Build.cs` 中需要添加：

```csharp
PublicIncludePaths.AddRange(new string[] {
    Path.Combine(ModuleDirectory, "Classes")
});
```

## Demo 示例

如果你想基于此插件创建自己的插件，步骤如下：

1. 复制 `UObjectPlugin` 目录到你的项目 `Plugins/` 下
2. 重命名目录和所有内部引用（模块名、类名等）
3. 在 `Build.cs` 中添加你的模块依赖
4. 在 `Classes/` 或 `Public/` 下添加你的 `UCLASS`

### Build.cs 模板

```csharp
// 来源: Source/UObjectPlugin/UObjectPlugin.Build.cs
public class UObjectPlugin : ModuleRules
{
    public UObjectPlugin(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
        });
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库（FString、TArray 等） |
| `CoreUObject` | UObject 系统（UCLASS、UPROPERTY 反射支持） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-10 | `abb369e` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 自动化代码修正工具批量添加，非人工维护 |
| 2023-01-16 | `bbc37aa` | Another batch iwyu updates to reduce number of includes | IWYU（Include What You Use）批量清理 |
| 2022-10-21 | `610c467` | Update vendor links for built-in plugins to use secure protocol | URL 协议从 http 更新到 https |

### 维护评价

- **创建时间**：2014 年 3 月，超过 11 年历史，属于 UE4 早期产物
- **更新频率**：近 3 次更新全部是自动化批量修正（IWYU、UE_INLINE_GENERATED_CPP_BY_NAME、URL 协议），没有功能性改动
- **实质更新**：自创建以来几乎没有实质性功能更新，说明此插件作为示例模板已非常稳定
- **状态**：🏛️ 文物级示例模板，代码结构自 UE4 时代至今基本未变
- **推荐使用**：✅ 适合作为插件开发的起点模板。虽然代码风格偏旧（如使用 `Classes/` 目录而非 `Public/`），但核心模式仍然有效。建议参考后根据最新 UE5 最佳实践进行调整。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/UObjectPlugin)
- [官方文档]()（无）
- [测试用例]()（无，此插件无测试）
