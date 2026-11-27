import type { Register } from 'claude-code'

const BAR = '#e0a82e' // amber
const BG = '#4a3b12'
const FG = '#ffffff'

export const register: Register = on => {
  on('ui.render', { component: 'UserMessage' }, ($, e, next) => {
    // only what the person typed (terminal or Remote Control); notifications, peers and plugins keep their own rows
    const mine = e.props.origin.kind === 'composer' || e.props.origin.kind === 'bridge'
    if (!mine) return next(e)

    const { Box, Text } = $.ui.resolve(e)

    return (
      <Box flexDirection="row" marginTop={1} marginBottom={1}>
        <Box width={1} flexShrink={0} backgroundColor={BAR} />
        <Box flexGrow={1} flexShrink={1} paddingX={1} paddingY={1} backgroundColor={BG}>
          <Text color={FG}>{e.props.text}</Text>
        </Box>
      </Box>
    )
  })
}
