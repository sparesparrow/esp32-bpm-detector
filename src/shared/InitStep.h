#pragma once

#include <cstdint>

namespace sparetools {
namespace bpm {

/**
 * @brief Base class for initialization steps in the OMS application framework
 * 
 * InitStep provides a standardized way to initialize components with proper
 * error handling and sequencing. Each step should implement the execute()
 * method and set the 'finished' flag when complete.
 */
class InitStep {
public:
    /**
     * @brief Constructor
     */
    InitStep() : finished(false) {}
    
    /**
     * @brief Virtual destructor
     */
    virtual ~InitStep() = default;
    
    /**
     * @brief Execute the initialization step
     * @return true if step completed successfully, false otherwise
     */
    virtual bool execute() = 0;
    
    /**
     * @brief Check if the initialization step is complete
     * @return true if finished, false if still in progress
     */
    bool isFinished() const { return finished; }
    
    /**
     * @brief Get the name of this initialization step
     * @return C-string with step name
     */
    virtual const char* getName() const = 0;
    
protected:
    bool finished;  ///< Set to true when initialization is complete
};

} // namespace bpm
} // namespace sparetools
