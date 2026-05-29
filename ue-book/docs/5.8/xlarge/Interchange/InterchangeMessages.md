# Interchange Messages

> 用于在 Interchange 资产导入/导出过程中传递警告、错误和信息性消息的模块。

| 属性 | 值 |
|---|---|
| 中文名 | 交换消息 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeMessages` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-06-01 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime/Source/Messages) | |

## 用途

Interchange Messages 是 Interchange 框架的子模块，专门负责定义资产导入/导出过程中产生的结构化消息类型。这些消息（如错误、警告、显示信息）用于在解析器、管线和用户界面之间传递详细的诊断信息，而不是简单的文本字符串。它使得消息可以携带上下文元数据（例如哪个网格或纹理出了问题），便于更精确地报告和处理问题。

## 使用场景

- **自定义资产导入流程**：当你需要监听或拦截 Interchange 框架在解析 FBX、GLTF 等文件时发出的具体警告或错误时。
- **构建导入日志与报告**：在导入完成后，遍历 `UInterchangeResult` 对象列表，获取结构化信息来生成详细的导入报告。
- **插件开发**：如果你正在为 Interchange 框架开发新的解析器或工厂节点，需要使用这些消息类来向框架报告处理状态。

## 蓝图用法

Interchange Messages 模块主要定义了用于携带信息的 UObject 类，这些类通常由 Interchange 框架内部在解析和导入过程中创建，并通过结果数组暴露。蓝图用户更多是作为消息的消费者，而非创建者。

### 核心节点

以下类定义在 `Public/Fbx/InterchangeFbxMessages.h` 中，代表了特定于 FBX 导入场景的结构化消息。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MeshName` | 获取与该消息相关的网格体的名称。 | `UInterchangeResultMeshWarning` |
| `TextureName` | 获取与该消息相关的纹理的名称。 | `UInterchangeResultTextureWarning` |
| `ExcessUVs` | 获取超出预期的 UV 通道数量。 | `UInterchangeResultMeshWarning_TooManyUVs` |

### 使用示例（蓝图描述）

1.  **获取导入结果**：在你的资产导入完成事件后，从 `UInterchangeImportAsset` 或类似对象的 `Results` 属性中获取一个 `UInterchangeResult` 对象的数组。
2.  **过滤特定消息**：遍历该数组，并使用 `Class` 筛选节点查找特定类型，例如 `UInterchangeResultMeshWarning`。
3.  **读取消息详情**：对于找到的每个结果对象，你可以调用 `GetText` 节点获取通用的描述文本。对于特定子类（如 `UInterchangeResultMeshWarning_TooManyUVs`），你还可以直接访问 `ExcessUVs` 属性，获取数值型上下文信息。

## C++ 用法

### 头文件引入

```cpp
#include “InterchangeFbxMessages.h”
```

### 基本用法

此模块的类主要用于声明和携带数据。以下是如何在代码中访问导入结果中的消息。

**示例：遍历并打印所有网格相关的警告** (源自常见的 Interchange 结果处理模式)

```cpp
// 假设你有一个导入后得到的结果数组
TArray<UInterchangeResult*> ImportResults = ...;

for (UInterchangeResult* Result : ImportResults)
{
    // 检查是否是特定的网格警告
    if (UInterchangeResultMeshWarning* MeshWarning = Cast<UInterchangeResultMeshWarning>(Result))
    {
        UE_LOG(LogTemp, Warning, TEXT(“Mesh ‘%s’ imported with warning: %s”),
            *MeshWarning->MeshName,
            *MeshWarning->GetText().ToString());
    }
    // 检查是否有 UV 过多的警告，并提取额外信息
    else if (UInterchangeResultMeshWarning_TooManyUVs* TooManyUVs = Cast<UInterchangeResultMeshWarning_TooManyUVs>(Result))
    {
        UE_LOG(LogTemp, Warning, TEXT(“Mesh ‘%s’ has %d excess UV channels.”),
            *TooManyUVs->MeshName,
            TooManyUVs->ExcessUVs);
    }
}
```

### 进阶用法

你可以继承这些消息类，为自己的自定义解析器或工厂创建具有更丰富上下文的特定消息类型。

```cpp
// 假设你在自定义的 GLTF 解析器中
UCLASS()
class UInterchangeResultMeshWarning_InvalidMaterial : public UInterchangeResultMeshWarning
{
    GENERATED_BODY()
public:
    UPROPERTY()
    FString MaterialName;

    virtual FText GetText() const override
    {
        return FText::Format(NSLOCTEXT(“MyPlugin”, “InvalidMat”, “Mesh {0} has invalid material {1}.“),
            FText::FromString(MeshName),
            FText::FromString(MaterialName));
    }
};

// 在你的解析逻辑中创建并添加这个消息
UInterchangeResultMeshWarning_InvalidMaterial* Warning = NewObject<UInterchangeResultMeshWarning_InvalidMaterial>(/* Outer */);
Warning->MeshName = TEXT(“Character_Mesh”);
Warning->MaterialName = TEXT(“M_Missing”);
Results.Add(Warning);
```

## Demo 示例

一个最小的示例，展示如何创建一个自定义的 Interchange 结果消息，并将其添加到结果数组中。

**MyCustomInterchangeMessage.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “InterchangeResult.h” // 基类所在的头文件，通常来自 InterchangeCommon 或 Messages 模块
#include “MyCustomInterchangeMessage.generated.h”

UCLASS(MinimalAPI)
class UInterchangeResultCustomDisplay_ImportNote : public UInterchangeResultDisplay_Generic
{
    GENERATED_BODY()

public:
    UPROPERTY()
    FString Note;

    virtual FText GetText() const override;
};
```

**MyCustomInterchangeMessage.cpp**
```cpp
#include “MyCustomInterchangeMessage.h”

FText UInterchangeResultCustomDisplay_ImportNote::GetText() const
{
    return FText::FromString(FString::Printf(TEXT(“Import Note: %s”), *Note));
}
```

**使用 (在你的解析器代码中)**
```cpp
// 在某个解析函数中
void UMyAssetParser::Parse(...)
{
    // ... 解析逻辑 ...

    // 创建一个提示信息
    if (SomeCondition)
    {
        UInterchangeResultCustomDisplay_ImportNote* Note = NewObject<UInterchangeResultCustomDisplay_ImportNote>();
        Note->Note = TEXT(“This asset has non-standard pivot point.”);
        Results.Add(Note);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InterchangeCommon` | 提供 `UInterchangeResult` 及其基类（`Error`, `Warning`, `Display`）的定义，是本模块所有消息类的基础。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-25 | `61d0e791` | USD Pregen: Implement tracking of Skeleton and PhysicsAssets | 为 USD 预生成添加骨架和物理资产跟踪，属于功能扩展 |
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复了 UE 5.8 版本中的本地化警告，属于维护性修复 |
| 2026-05-22 | `8fdd3a89` | [Interchange] Reset existing LODModels for reimport, so that Bone bindings and mappings are updated | 修复了重新导入时LOD模型和骨骼绑定的更新问题，属于核心功能修复 |
| 2026-05-22 | `3cfa4417` | Reinstated the uFBX parser as experimental | 将 uFBX 解析器重新标记为实验性，影响框架的解析器选项 |
| 2026-05-19 | `755f95d4` | Interchange: Fix crash by protecting against nullptr objects in the list of imported objects. | 修复了导入对象列表中空指针导致的崩溃，属于稳定性修复 |

### 维护评价

**活跃维护**。Interchange 是 Epic 用于替换旧版资产导入管线的下一代框架，是 UE5 的核心模块之一。从 Git 记录看，最近数月内有持续的功能开发、兼容性修复和稳定性改进。`InterchangeMessages` 作为框架的基础通信模块，会随着主框架同步更新。该模块结构稳定，接口成熟，**强烈推荐**在进行自定义资产导入开发或需要深度集成 Interchange 框架时使用。

## 相关链接

- [源码 (InterchangeMessages)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime/Source/Messages)
- [源码 (Interchange 主框架)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange)
- [测试用例 (Engine/Tests/Interchange)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Interchange)