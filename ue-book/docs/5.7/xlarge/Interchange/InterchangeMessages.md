# Interchange Framework – InterchangeMessages 模块

> 本模块是 Interchange 插件的一部分，定义了导入/导出过程中生成的各类结果消息（警告、错误、显示信息）。

| 属性 | 值 |
|---|---|
| 中文名 | 交换框架消息模块 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeMessages` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime/Source/Messages) | |

## 用途

InterchangeMessages 提供了一组 UObject 类，用于表示导入/导出管线中产生的各种结果（Result）。它定义了基础类层次结构：

- `UInterchangeResult` → `UInterchangeResultWarning` / `UInterchangeResultError` / `UInterchangeResultDisplay_Generic`
- 进一步派生出与具体解析器相关的子类，例如 `UInterchangeResultMeshWarning`、`UInterchangeResultTextureWarning` 等。

这些消息携带结构化的元数据（如 `MeshName`、`TextureName`）以及人类可读的文本，方便 UI 显示或日志记录。通过继承这些基类，开发者可以自定义消息类型，从而在导入流程中精确传递错误或警告信息。

## 使用场景

- **自定义导入管线**：当你为 Interchange 编写自定义解析器或 Pipeline 时，需要生成特定类型的消息（如几何体警告、材质错误）。
- **诊断与调试**：在导入资产后，遍历 `UInterchangeResultsContainer` 中的消息，提取其中的文本和元数据，用于 UI 反馈或自动化测试。

## 蓝图用法

本模块中的类均为数据容器（UObject），没有公开的 BlueprintCallable 函数。但蓝图中可以获取这些消息实例的 `Text`、`MeshName` 等属性（`UPROPERTY`，默认 BlueprintReadWrite）。

例如：

- `UInterchangeResultMeshWarning_Generic` 的 `Text` 属性可以在蓝图中直接读取或赋值。

**注意**：实际使用中，消息实例通常由 C++ 代码创建并添加到结果容器中，蓝图主要用于展示或处理这些消息。

## C++ 用法

### 头文件引入

```cpp
#include "Fbx/InterchangeFbxMessages.h"
#include "InterchangeResult.h"
```

### 基本用法

创建自定义警告消息并添加到结果容器：

```cpp
// 假设已有结果容器指针 ResultContainer (UInterchangeResultsContainer*)
UInterchangeResultMeshWarning_Generic* Warning = NewObject<UInterchangeResultMeshWarning_Generic>();
Warning->MeshName = TEXT("MyMesh");
Warning->Text = FText::FromString(TEXT("Missing UV2 channel on mesh."));
ResultContainer->AddMessage(Warning);
```

### 进阶用法

实现自定义消息类，继承自 `UInterchangeResultWarning` 并增加特定字段：

```cpp
// CustomResult.h
#include "InterchangeResult.h"
#include "CustomResult.generated.h"

UCLASS()
class UCustomImportWarning : public UInterchangeResultWarning
{
    GENERATED_BODY()
public:
    UPROPERTY()
    FString MaterialName;

    virtual FText GetText() const override
    {
        return FText::Format(NSLOCTEXT("CustomImport", "CustomWarning", "Material {0} has missing texture."), FText::FromString(MaterialName));
    }
};
```

在导入管线中提交此消息，UI 会自动根据类型显示图标和文本。

## Demo 示例

一个完整的最小示例，展示如何创建消息并输出其文本：

### CustomMessageDemo.h

```cpp
#pragma once
#include "CoreMinimal.h"
#include "InterchangeResult.h"
#include "CustomMessageDemo.generated.h"

UCLASS()
class UCustomMessageDemo : public UObject
{
    GENERATED_BODY()
public:
    UFUNCTION()
    void RunDemo();
};
```

### CustomMessageDemo.cpp

```cpp
#include "CustomMessageDemo.h"
#include "Fbx/InterchangeFbxMessages.h"

void UCustomMessageDemo::RunDemo()
{
    // 创建一个通用网格警告
    UInterchangeResultMeshWarning_Generic* Warning = NewObject<UInterchangeResultMeshWarning_Generic>();
    Warning->MeshName = TEXT("Cube");
    Warning->Text = FText::FromString(TEXT("Cube has no smoothing groups."));

    // 模拟添加到结果容器（实际使用中容器由管线管理）
    FString Output = FString::Printf(TEXT("[%s] %s: %s"), *Warning->GetType()->GetName(), *Warning->MeshName, *Warning->Text.ToString());
    UE_LOG(LogTemp, Warning, TEXT("%s"), *Output);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Engine` | 提供 Core、UObject、反射系统等基础支持 |

**无特殊依赖**（仅标准 Core/Engine）。

## 维护状态

### 近期更新

- 2025-12-18 `93cfc06e` — Fixed editor hanging when level reimporting a file containing skeletal meshes
- 2025-10-23 `0158cf6a` — [Interchange] Removing unintended LOD specialization from named LOD Groups.
- 2025-10-21 `63c630c0` — [Interchange] Fixing missing animation sequence import for LevelSequence on StaticMesh imported with …
- 2025-10-17 `765b3a10` — Fixed compilation error with NonUnity InterchangeWorker
- 2025-10-17 `2c91170f` — Replaced use of /InterchangeAssets/Materials/PhongSurfaceMaterial.PhongSurfaceMaterial with /Interch …

### 维护评价

模块创建于 2025-10-17，至今不足半年，属于全新模块。最近一次功能性更新在 2025-12-18（修复编辑器卡死），表明项目处于活跃维护阶段。无已知废弃或不稳定标记。推荐用于基于 Interchange 的导入/导出开发。

## 相关链接

- [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime/Source/Messages)
- [Interchange 插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/interchange-framework/)（需确认）