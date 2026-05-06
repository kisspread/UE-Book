# NNEMlirTools

> A runtime implementing the Neural Network Engine (NNE) API which is based on IREE, MLIR and LLVM and compiles neural networks directly to game code.

| 属性 | 值 |
|---|---|
| 中文名 | MLIR 模型检查工具 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `IREEUtils` (Runtime), `IREEDriverRDG` (Runtime), `NNERuntimeIREE` (Runtime), `NNERuntimeIREEEditor` (Editor), `NNERuntimeIREEShader` (Runtime), `IREE` (External), `NNEMlirTools` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE) | |

## 用途

`NNEMlirTools` 是一个轻量级的 MLIR 模块结构检查工具，属于 NNERuntimeIREE 插件。它提供一个纯 C 的 API 和一个可选的 C++ 包装，用于解析和只读检查 MLIR 模块中的公共函数签名、输入输出张量的名称、数据类型和形状。该工具不执行推理，仅用于静态模型结构分析，是 NNERuntimeIREE 编译管线中获取模型元数据的关键组件。

## 使用场景

- 在 NNERuntimeIREE 中加载编译后的神经网络模型时，需提前获取输入/输出张量的维度和类型以分配缓冲区。
- 离线工具链中解析 MLIR 文件，提取函数原型用于代码生成或验证。
- 在其他 UE 模块中需要解析 MLIR 表示时，可作为轻量内省库使用。

## 蓝图用法

`NNEMlirTools` 是纯 C/C++ 库，不提供 BlueprintCallable 函数。建议将其封装在 C++ 模块中，再通过 UFUNCTION 暴露给蓝图（例如在 `NNERuntimeIREE` 模块的 `UNNERuntimeIREE` 类中已存在类似封装），当前模块自身无蓝图节点。

## C++ 用法

### 头文件引入

```cpp
// C 接口
#include "Internal/NNEMlirTools.h"

// C++ 包装接口（可选）
#include "Internal/NNEMlirTools_cxx_api.h"
```

### 基本用法

以下示例演示使用纯 C API 解析 MLIR 文件并打印函数信息：

```cpp
// 文件：Engine/Plugins/Experimental/NNERuntimeIREE/Source/ThirdParty/NNEMlirTools/Test/TestExample.cpp
// 说明：假设已有 MLIR 文件路径

#include "Internal/NNEMlirTools.h"
#include <iostream>
#include <vector>

int main() {
    // 1. 获取 API 接口（版本校验）
    const NNEMlirApi* Api = NNEMlirGetInterface(NNEMLIR_ABI_VERSION);
    if (!Api) {
        std::cerr << "NNEMlirTools API version mismatch!" << std::endl;
        return 1;
    }

    // 2. 创建上下文
    NNEMlirContext Ctx = Api->CreateContext();
    NNEMlirStatus Sts = nullptr;
    NNEMlirModule Mod = nullptr;

    // 3. 从文件解析
    Sts = Api->ParseModuleFromFile(Ctx, "/path/to/model.mlir", &Mod);
    if (Api->GetStatusCode(Sts) != NNEMLIR_SUCCESS) {
        std::cerr << "Parse failed: " << Api->StatusToString(Sts) << std::endl;
        Api->ReleaseStatus(Sts);
        Api->ReleaseContext(Ctx);
        return 1;
    }
    Api->ReleaseStatus(Sts);

    // 4. 遍历公共函数
    size_t FuncCount = Api->GetPublicFunctionCount(Mod);
    for (size_t i = 0; i < FuncCount; ++i) {
        NNEMlirFunction Func = Api->GetPublicFunction(Mod, i);
        const char* Name = Api->GetFunctionName(Func);
        std::cout << "Function: " << Name << std::endl;

        // 输入参数
        size_t InputCount = Api->GetInputCount(Func);
        for (size_t j = 0; j < InputCount; ++j) {
            NNEMlirValue Val = Api->GetInputValue(Func, j);
            const char* ValName = Api->GetValueName(Val);
            const char* TypeText = Api->GetValueTypeText(Val);
            const char* ElemType = Api->GetElementTypeText(Val);
            std::vector<int64_t> Shape(8);
            size_t Rank = Api->GetShape(Val, Shape.data(), Shape.size());
            Shape.resize(Rank);
            std::cout << "  Input " << j << ": name=" << (ValName ? ValName : "(unnamed)")
                      << ", type=" << TypeText
                      << ", element=" << ElemType
                      << ", shape=[";
            for (size_t d = 0; d < Rank; ++d)
                std::cout << (d ? ", " : "") << Shape[d];
            std::cout << "]" << std::endl;
            Api->ReleaseValue(Val);
        }

        // 输出结果
        size_t ResultCount = Api->GetResultCount(Func);
        for (size_t j = 0; j < ResultCount; ++j) {
            NNEMlirValue Val = Api->GetResultValue(Func, j);
            // ... 类似处理
            Api->ReleaseValue(Val);
        }

        Api->ReleaseFunction(Func);
    }

    // 5. 清理
    Api->ReleaseModule(Mod);
    Api->ReleaseContext(Ctx);
    return 0;
}
```

### 进阶用法

使用 C++ 包装 API（`NNEMlirTools_cxx_api.h`）可自动管理资源并简化异常处理：

```cpp
#include "Internal/NNEMlirTools_cxx_api.h"
#include <iostream>

int main() {
    // 初始化 API（需在程序启动时调用一次）
    const NNEMlirApi* BaseApi = NNEMlirGetInterface(NNEMLIR_ABI_VERSION);
    NNEMlirTools::Api::Initialize(BaseApi);

    try {
        // 使用 C++ 智能句柄（UniqueHandle）
        NNEMlirTools::UniqueHandle<NNEMlirContext> Ctx(NNEMlirTools::Api::Instance()->CreateContext());

        // 解析并获取 Module 句柄（UniqueHandle 自动释放）
        NNEMlirTools::UniqueHandle<NNEMlirModule> Mod;
        NNEMlirTools::UniqueHandle<NNEMlirStatus> Sts;
        Sts = NNEMlirTools::MakeHandle(NNEMlirTools::Api::Instance()->ParseModuleFromFile(
            Ctx.Get(), "/path/to/model.mlir", Mod.ResetAndGetAddressOf()));

        if (NNEMlirTools::Api::Instance()->GetStatusCode(Sts.Get()) != NNEMLIR_SUCCESS) {
            throw std::runtime_error(NNEMlirTools::Api::Instance()->StatusToString(Sts.Get()));
        }

        // 使用迭代器风格访问
        size_t Count = NNEMlirTools::Api::Instance()->GetPublicFunctionCount(Mod.Get());
        for (size_t i = 0; i < Count; ++i) {
            auto Func = NNEMlirTools::MakeHandle(NNEMlirTools::Api::Instance()->GetPublicFunction(Mod.Get(), i));
            std::cout << "Function: " << NNEMlirTools::Api::Instance()->GetFunctionName(Func.Get()) << std::endl;
        }
    } catch (const std::exception& E) {
        std::cerr << "Error: " << E.what() << std::endl;
        return 1;
    }
    return 0;
}
```

## Demo 示例

完整的最小可编译示例代码（基于 C API，不依赖 UE 模块）：

```cpp
// MyMLIRInspector.h
#pragma once
#include <string>
#include <vector>

class FMLIRInspector {
public:
    bool Initialize();
    bool Parse(const char* FilePath);
    void PrintSummary();

private:
    const NNEMlirApi* Api = nullptr;
    NNEMlirContext Ctx = nullptr;
    NNEMlirModule Mod = nullptr;
};
```

```cpp
// MyMLIRInspector.cpp
#include "MyMLIRInspector.h"
#include <iostream>

bool FMLIRInspector::Initialize() {
    Api = NNEMlirGetInterface(NNEMLIR_ABI_VERSION);
    return Api != nullptr;
}

bool FMLIRInspector::Parse(const char* FilePath) {
    if (!Api) return false;
    Ctx = Api->CreateContext();
    NNEMlirStatus Sts = nullptr;
    if (Api->ParseModuleFromFile(Ctx, FilePath, &Mod) != NNEMLIR_SUCCESS) {
        Api->ReleaseContext(Ctx);
        Ctx = nullptr;
        return false;
    }
    return true;
}

void FMLIRInspector::PrintSummary() {
    if (!Api || !Mod) return;
    size_t FuncCount = Api->GetPublicFunctionCount(Mod);
    std::cout << "Module has " << FuncCount << " public functions." << std::endl;
    // 详细打印略…
}
```

## 模块依赖

`NNEMlirTools` 作为 External 模块，不依赖 UE 核心模块。其底层链接 IREE/MLIR/LLVM 库（在 IREE 第三方模块中提供）。在 Build.cs 中，其他模块若使用 `NNEMlirTools` 需在 `PublicDependencyModuleNames` 中添加 `"NNEMlirTools"`。此外 `NNERuntimeIREE` 模块已自动处理此依赖，因此用户通常无需直接引用。

## 维护状态

### 近期更新

- 2025-09-26 `e0d52775` [NNE] NNERuntime IREE support of path with spaces on RelTest build on Mac for RDG.
- 2025-09-24 `ca784fe6` [NNE] NNERuntimeIREERdg always prefer wave32 to be consistent with used GPU profiles from IREE.
- 2025-09-24 `1dc2a8b6` [NNE] NNERuntimeIREE fix typo in Linux build script.
- 2025-09-24 `08183aae` [NNE] NNERuntime IREE support of path with spaces on RelTest build on Mac.
- 2025-09-12 `f4a4fff3` [NNE] NNERuntimeIREE fix onnx importer dependencies not staged for Engine installed build.

### 维护评价

- 创建于 2025-09-12，至今不到一个月，属于全新插件。
- 最近更新活跃（连续多天修复），且属于游戏引擎核心 ML 特性，收重视程度高。
- 当前为实验性版本（IsExperimentalVersion=true），API 可能变化。
- 已知限制：平台只支持 Win64 x64，不支持 arm64；非线程安全（文档写明）。
- 推荐使用场景：仅用于探索性开发，不建议直接用于生产项目，待插件稳定后考虑。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE/Source/ThirdParty/NNEMlirTools)（无独立测试目录，可参考 NNERuntimeIREE 的自动化测试）