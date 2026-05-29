# OpenCV

> Plugin initializing OpenCV library to be used in engine.

| 属性 | 值 |
|---|---|
| 中文名 | 计算机视觉库 |
| 分类 | Computer Vision |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（OpenCV 库头文件、Python 脚本依赖） |
| 模块 | `OpenCVHelper` (Runtime), `OpenCV` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-11-22 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenCV) | |

## 用途

该插件将 OpenCV（开源计算机视觉库）集成到 Unreal Engine 中，提供计算机视觉功能的 C++ 和 Python 接口。插件包含两部分核心内容：

1. **OpenCVHelper 运行时模块**：封装层，为引擎提供 OpenCV 功能的统一接口
2. **ThirdParty OpenCV 库**：OpenCV 4.5.5 的预编译头文件和静态库

同时通过 PythonRequirements 提供 `opencv-python==4.5.5.62` 的 Python 绑定，支持在编辑器中通过 Python 脚本调用 OpenCV 功能。

该插件存在的意义是将之前散落在引擎各处（如相机标定相关代码）的 OpenCV 依赖统一归口管理，并作为未来扩展更多计算机视觉工具的基础。

## 使用场景

- 你需要对摄像机画面进行实时图像处理（滤波、边缘检测、色彩空间转换）→ 用 OpenCV
- 你需要进行相机标定或手眼标定 → 用 OpenCV
- 你需要在编辑器 Python 脚本中进行图像分析（批量处理纹理、检测特征点）→ 用 OpenCV 的 Python 绑定
- 你需要实现目标检测、模板匹配等视觉算法 → 用 OpenCV
- 你需要从摄像头或视频文件捕获帧数据 → 用 OpenCV 的 VideoCapture

## 蓝图用法

该插件主要面向 C++ 和 Python 使用场景，不提供蓝图公开接口（BlueprintCallable/BlueprintReadWrite）。

## C++ 用法

### 头文件引入

```cpp
#include "OpenCVHelper.h"
```

OpenCV 库本身的头文件引入方式：

```cpp
#include "opencv2/core/core.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/calib3d/calib3d.hpp"
```

### 基本用法

OpenCV 4.x C++ API 使用 cv::Mat 作为核心数据结构：

```cpp
#include "opencv2/core/core.hpp"
#include "opencv2/imgproc/imgproc.hpp"

void ProcessImage()
{
    // 创建一个 640x480 的 BGR 图像
    cv::Mat image(480, 640, CV_8UC3, cv::Scalar(0, 0, 255));
    
    // 灰度转换
    cv::Mat gray;
    cv::cvtColor(image, gray, cv::COLOR_BGR2GRAY);
    
    // 高斯模糊
    cv::Mat blurred;
    cv::GaussianBlur(gray, blurred, cv::Size(5, 5), 1.5);
    
    // Canny 边缘检测
    cv::Mat edges;
    cv::Canny(blurred, edges, 50, 150);
}
```

### C API 用法（legacy）

OpenCV 仍保留了 C 语言兼容 API（通过 `_c.h` 后缀头文件），用于处理 IplImage 等传统数据结构：

```cpp
#include "opencv2/core/core_c.h"
#include "opencv2/imgproc/imgproc_c.h"
#include "opencv2/highgui/highgui_c.h"

// 创建 IplImage
IplImage* img = cvCreateImage(cvSize(640, 480), IPL_DEPTH_8U, 3);

// C API 滤波
cvSmooth(img, img, CV_GAUSSIAN, 3, 3, 0, 0);

// 释放
cvReleaseImage(&img);
```

### 进阶用法

相机标定（Calibration）是该插件的原始核心用途之一：

```cpp
#include "opencv2/calib3d/calib3d.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include <vector>

void CalibrateCamera(
    const std::vector<std::vector<cv::Point2f>>& imagePoints,
    const std::vector<std::vector<cv::Point3f>>& objectPoints,
    cv::Size imageSize)
{
    cv::Mat cameraMatrix, distCoeffs;
    std::vector<cv::Mat> rvecs, tvecs;
    
    // 使用 OpenCV 进行相机标定
    double rms = cv::calibrateCamera(
        objectPoints, imagePoints, imageSize,
        cameraMatrix, distCoeffs, rvecs, tvecs,
        cv::CALIB_FIX_ASPECT_RATIO | cv::CALIB_ZERO_TANGENT_DIST
    );
}

// 使用 FLANN 进行特征点匹配
void MatchFeatures(const cv::Mat& descriptors1, const cv::Mat& descriptors2)
{
    cv::flann::IndexParams indexParams;
    indexParams.setAlgorithm(cvflann::FLANN_INDEX_KDTREE);
    indexParams.setInt("trees", 5);
    
    cv::flann::SearchParams searchParams;
    searchParams.setAlgorithm(cvflann::FLANN_INDEX_KDTREE);
    searchParams.setAlgorithm(32);
    
    cv::FlannBasedMatcher matcher(indexParams, searchParams);
    std::vector<cv::DMatch> matches;
    matcher.match(descriptors1, descriptors2, matches);
}
```

## Demo 示例

以下是一个完整的最小示例，展示如何在 UE5 模块中使用 OpenCV 进行图像处理：

### MyVisionModule.h

```cpp
#pragma once

#include "CoreMinimal.h"

class FMyVisionModule
{
public:
    // 将 UTexture2D 转换为 cv::Mat（简化示例）
    static bool TextureToMat(UTexture2D* Texture, cv::Mat& OutMat);
    
    // 对 cv::Mat 进行边缘检测并返回结果
    static cv::Mat DetectEdges(const cv::Mat& InputImage, double Threshold1 = 50.0, double Threshold2 = 150.0);
    
    // 从 cv::Mat 创建 UTexture2D（简化示例）
    static UTexture2D* MatToTexture(const cv::Mat& Mat);
};
```

### MyVisionModule.cpp

```cpp
#include "MyVisionModule.h"
#include "opencv2/core/core.hpp"
#include "opencv2/imgproc/imgproc.hpp"

bool FMyVisionModule::TextureToMat(UTexture2D* Texture, cv::Mat& OutMat)
{
    if (!Texture) return false;
    
    const int32 Width = Texture->GetSizeX();
    const int32 Height = Texture->GetSizeY();
    
    // 获取纹理数据
    FTexture2DMipMap& Mip = Texture->GetPlatformData()->Mips[0];
    void* Data = Mip.BulkData.Lock(LOCK_READ_WRITE);
    
    // 创建 OpenCV Mat（BGRA 格式）
    cv::Mat BGRA(Height, Width, CV_8UC4, Data);
    cv::cvtColor(BGRA, OutMat, cv::COLOR_BGRA2BGR);
    
    Mip.BulkData.Unlock();
    return true;
}

cv::Mat FMyVisionModule::DetectEdges(const cv::Mat& InputImage, double Threshold1, double Threshold2)
{
    cv::Mat Gray, Edges;
    
    // 转灰度
    cv::cvtColor(InputImage, Gray, cv::COLOR_BGR2GRAY);
    
    // 高斯模糊降噪
    cv::GaussianBlur(Gray, Gray, cv::Size(3, 3), 0);
    
    // Canny 边缘检测
    cv::Canny(Gray, Edges, Threshold1, Threshold2);
    
    return Edges;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PythonFoundationPackages` | Python 环境基础（仅编辑器） |
| OpenCV 4.5.5 第三方库 | 图像处理、特征检测、相机标定等计算机视觉功能 |

无特殊运行时模块依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF 新格式 |
| 2026-04-13 | `a0b7804f` | [OpenCV] Add OpenCV library for macOS | 为 macOS 平台添加 OpenCV 库支持 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理纹理属性修改代码，正确使用 PreEditChange/PostEditChange 包装 |
| 2025-11-10 | `e0906b79` | Fix for crash when OpenCV fails to load | 修复 OpenCV 加载失败时的崩溃问题 |

### 维护评价

**维护中**。该插件虽然标记为实验性（IsBetaVersion=true），但近 6 个月内有多次实质性更新，包括平台扩展（macOS 支持）、编译问题修复和稳定性改进。创建于 2021 年 UE5 初期，最初是为了统一管理 OpenCV 依赖。

**主要注意事项**：
- **默认未启用**（EnabledByDefault=false），需要在项目设置中手动启用
- **实验性标记**（IsBetaVersion=true），API 可能在未来版本中变化
- 依赖 `opencv-python==4.5.5.62` 的特定哈希版本，更新 OpenCV 版本需要同步修改
- Python 绑定仅在编辑器中可用（PythonFoundationPackages 的 TargetAllowList 为 Editor）

**推荐使用**：如果你需要在 UE5 项目中进行计算机视觉相关工作（图像处理、相机标定、特征匹配等），该插件是首选方案。但需要注意其实验性状态，建议在生产环境中做好版本锁定和测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenCV)
- [OpenCV 官方文档](https://docs.opencv.org/4.5.5/)（第三方库文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenCV/Source)